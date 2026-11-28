<?php
/**
 * Centralized HTTP Client, HMAC-SHA256 Signer, and UI Error Mapper for AgroTracer Bridge
 *
 * Implements Epic [EP-S1] Sprint 1 — Data & Identity Foundation (Task S1-T04 / ADR-002):
 * - Native WordPress HTTP API (`wp_remote_get`, `wp_remote_post`) with explicit defensive timeout.
 * - Strict server-side actor resolution via `get_current_user_id()` after `wp_verify_nonce()`
 *   and `current_user_can()` verification (never accepts `user_id` from browser/request payloads).
 * - Mandatory authentication and distributed tracing headers:
 *   `X-AgroTracer-Actor-ID`, `X-AgroTracer-User-Id`, `X-AgroTracer-Timestamp`,
 *   `X-AgroTracer-Nonce`, `X-AgroTracer-Signature`, `X-Correlation-ID`.
 * - Non-leaky, user-friendly UI error mapping for FastAPI/PostgreSQL status codes
 *   (400, 401, 403, 404, 409, 422, 429, 500, 503).
 *
 * @package AgroTracerBridge
 * @version 3.1.0
 */

declare(strict_types=1);

namespace AgroTracerBridge\Http;

use InvalidArgumentException;
use RuntimeException;

if (!defined('ABSPATH')) {
    exit;
}

/**
 * Class AgroTracer_Http_Client
 *
 * Centralized server-to-server HTTP client for communicating between WordPress
 * and the Python FastAPI backend over the signed HMAC-SHA256 bridge.
 */
class AgroTracer_Http_Client {

    /**
     * Maximum allowed clock skew in seconds (±300s window per ADR-002).
     */
    public const TIMESTAMP_TOLERANCE_SECONDS = 300;

    /**
     * Nonce retention TTL in seconds (600s full window + 60s safety margin per ADR-002).
     */
    public const NONCE_TTL_SECONDS = 660;

    /**
     * Reserved system user identifier (0) for internal routines.
     * Business routes strictly require authenticated WordPress users (> 0).
     */
    public const SYSTEM_USER_ID = 0;

    /**
     * Default defensive HTTP timeout in seconds for WordPress remote requests.
     */
    public const DEFAULT_TIMEOUT_SECONDS = 10;

    /**
     * Default required WordPress capability for producer operations.
     */
    public const DEFAULT_REQUIRED_CAPABILITY = 'agrotracer_manage_farms';

    /**
     * Normalizes URI path and query string strictly according to RFC 3986 (ADR-002).
     * Guarantees 100% deterministic parity with Python's `normalizar_path_query()`.
     *
     * @param string $path_with_query Relative path and optional query string (must start with `/`).
     * @return string Normalized RFC 3986 path and sorted query string.
     * @throws InvalidArgumentException If fragments, scheme/host, or invalid UTF-8 sequences are present.
     */
    public static function normalize_path_query(string $path_with_query): string {
        if (strpos($path_with_query, '#') !== false) {
            throw new InvalidArgumentException('Fragmentos não são permitidos na URI da Bridge.');
        }

        $parts = parse_url($path_with_query);
        if (
            $parts === false ||
            isset($parts['scheme']) ||
            isset($parts['host']) ||
            strpos($path_with_query, '//') === 0
        ) {
            throw new InvalidArgumentException('A URI deve conter apenas path relativo e query string.');
        }

        $path = $parts['path'] ?? '';
        if (strpos($path, '/') !== 0) {
            throw new InvalidArgumentException("O path da requisição deve começar com '/'.");
        }

        if (preg_match('//u', $path) !== 1) {
            throw new InvalidArgumentException('Sequência UTF-8 inválida detectada no path.');
        }

        $query = $parts['query'] ?? '';
        if ($query === '') {
            return $path;
        }

        $raw_pairs = explode('&', $query);
        $parameters = [];
        $idx = 0;

        foreach ($raw_pairs as $pair) {
            if ($pair === '') {
                continue;
            }

            $eq_pos = strpos($pair, '=');
            if ($eq_pos === false) {
                $key = urldecode($pair);
                $val = '';
            } else {
                $key = urldecode(substr($pair, 0, $eq_pos));
                $val = urldecode(substr($pair, $eq_pos + 1));
            }

            if (preg_match('//u', $key) !== 1 || preg_match('//u', $val) !== 1) {
                throw new InvalidArgumentException('Sequência UTF-8 inválida detectada na query string.');
            }

            $parameters[] = [
                'key' => $key,
                'val' => $val,
                'idx' => $idx++,
            ];
        }

        if (empty($parameters)) {
            return $path;
        }

        // Stable alphabetical sort by key (matches Python's Timsort behavior)
        usort($parameters, static function (array $a, array $b): int {
            $cmp = strcmp($a['key'], $b['key']);
            return $cmp !== 0 ? $cmp : ($a['idx'] <=> $b['idx']);
        });

        $encoded_pairs = array_map(static function (array $item): string {
            return rawurlencode($item['key']) . '=' . rawurlencode($item['val']);
        }, $parameters);

        return $path . '?' . implode('&', $encoded_pairs);
    }

    /**
     * Builds the canonical payload string for HMAC-SHA256 computation.
     *
     * Format:
     * METHOD\nPATH_WITH_QUERY\nTIMESTAMP\nNONCE\nACTOR_ID\nSHA256_HEX(RAW_BODY)
     *
     * @param string $method          HTTP verb (GET, POST, PUT, DELETE, etc.).
     * @param string $path_with_query Relative URI path and query string.
     * @param int    $timestamp       UNIX UTC timestamp in seconds.
     * @param string $nonce           Unique cryptographic nonce.
     * @param int    $actor_id        Authenticated WordPress user ID resolved server-side.
     * @param string $raw_body        Raw JSON payload string (empty string for GET).
     * @return string Canonical multiline string encoded in UTF-8.
     * @throws InvalidArgumentException If actor ID or URI format is invalid.
     */
    public static function build_canonical_string(
        string $method,
        string $path_with_query,
        int $timestamp,
        string $nonce,
        int $actor_id,
        string $raw_body = ''
    ): string {
        if ($actor_id < 0) {
            throw new InvalidArgumentException('O identificador do ator deve ser um inteiro não negativo.');
        }

        $normalized_method = strtoupper(trim($method));
        if ($normalized_method === '') {
            throw new InvalidArgumentException('O método HTTP não pode ser vazio.');
        }

        $normalized_uri = self::normalize_path_query($path_with_query);
        $body_sha256    = hash('sha256', $raw_body);

        return implode("\n", [
            $normalized_method,
            $normalized_uri,
            (string) $timestamp,
            $nonce,
            (string) $actor_id,
            $body_sha256,
        ]);
    }

    /**
     * Computes the lowercase hexadecimal HMAC-SHA256 signature (64 characters).
     *
     * @param string $canonical_string Canonical payload string.
     * @param string $secret_key       Shared HMAC secret key (min 32 ASCII bytes).
     * @return string 64-character lowercase hex HMAC-SHA256 signature.
     * @throws InvalidArgumentException If secret key is empty.
     */
    public static function compute_hmac_signature(string $canonical_string, string $secret_key): string {
        if (trim($secret_key) === '') {
            throw new InvalidArgumentException('O segredo criptográfico HMAC não pode ser vazio.');
        }

        return hash_hmac('sha256', $canonical_string, $secret_key);
    }

    /**
     * Generates a cryptographically secure 128-bit random nonce (32 lowercase hex characters)
     * for anti-replay protection.
     *
     * @return string 32-character hexadecimal nonce.
     */
    public static function generate_nonce(): string {
        return bin2hex(random_bytes(16));
    }

    /**
     * Resolves or generates a canonical lowercase UUIDv4 `X-Correlation-ID` (36 characters)
     * for end-to-end distributed tracing.
     *
     * @param string|null $incoming_id Optional incoming correlation ID header.
     * @return string Validated lowercase UUIDv4 string.
     */
    public static function resolve_correlation_id(?string $incoming_id = null): string {
        if (is_string($incoming_id)) {
            $candidate = strtolower(trim($incoming_id));
            if (preg_match('/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/', $candidate) === 1) {
                return $candidate;
            }
        }

        if (function_exists('wp_generate_uuid4')) {
            return strtolower((string) wp_generate_uuid4());
        }

        return sprintf(
            '%04x%04x-%04x-4%03x-%04x-%04x%04x%04x',
            random_int(0, 0xffff),
            random_int(0, 0xffff),
            random_int(0, 0xffff),
            random_int(0, 0x0fff),
            random_int(0, 0x3fff) | 0x8000,
            random_int(0, 0xffff),
            random_int(0, 0xffff),
            random_int(0, 0xffff)
        );
    }

    /**
     * Resolves the shared HMAC secret from `wp-config.php` constants or environment variables.
     * Supports both `AGROTRACER_API_HMAC_SECRET` and `AGROTRACER_BRIDGE_SECRET`.
     * Never exposes the secret to frontend HTML, templates, or JavaScript bundles.
     *
     * @return string Validated ASCII secret key (>= 32 bytes).
     * @throws RuntimeException If no valid secret is configured in non-development environments.
     */
    public static function resolve_hmac_secret(): string {
        $candidates = [];

        if (defined('AGROTRACER_API_HMAC_SECRET') && is_string(AGROTRACER_API_HMAC_SECRET)) {
            $candidates[] = AGROTRACER_API_HMAC_SECRET;
        }

        if (defined('AGROTRACER_BRIDGE_SECRET') && is_string(AGROTRACER_BRIDGE_SECRET)) {
            $candidates[] = AGROTRACER_BRIDGE_SECRET;
        }

        $env_hmac = getenv('AGROTRACER_API_HMAC_SECRET');
        if (is_string($env_hmac) && $env_hmac !== '') {
            $candidates[] = $env_hmac;
        }

        $env_bridge = getenv('AGROTRACER_BRIDGE_SECRET');
        if (is_string($env_bridge) && $env_bridge !== '') {
            $candidates[] = $env_bridge;
        }

        foreach ($candidates as $secret) {
            if (preg_match('/^[\x00-\x7F]{32,}$/', $secret) === 1) {
                return $secret;
            }
        }

        $app_env = defined('WP_ENVIRONMENT_TYPE') ? (string) WP_ENVIRONMENT_TYPE : (string) getenv('APP_ENV');
        if (in_array($app_env, ['production', 'staging'], true)) {
            throw new RuntimeException('Segredo HMAC da Bridge ausente ou inválido no servidor.');
        }

        // Fallback restricted strictly to local development and automated test suites
        return 'agrotracer_chave_exclusivamente_teste_2026';
    }

    /**
     * Resolves the FastAPI base URL from `wp-config.php` constants (`AGROTRACER_API_URL`
     * or `AGROTRACER_API_BASE_URL`) or environment variables.
     *
     * @return string Base URL without trailing slash.
     */
    public static function resolve_api_base_url(): string {
        if (defined('AGROTRACER_API_URL') && is_string(AGROTRACER_API_URL) && trim(AGROTRACER_API_URL) !== '') {
            return rtrim(trim(AGROTRACER_API_URL), '/');
        }

        if (defined('AGROTRACER_API_BASE_URL') && is_string(AGROTRACER_API_BASE_URL) && trim(AGROTRACER_API_BASE_URL) !== '') {
            return rtrim(trim(AGROTRACER_API_BASE_URL), '/');
        }

        $env_url = getenv('AGROTRACER_API_URL') ?: getenv('AGROTRACER_API_BASE_URL');
        if (is_string($env_url) && trim($env_url) !== '') {
            return rtrim(trim($env_url), '/');
        }

        return 'http://127.0.0.1:8000';
    }

    /**
     * Resolves the defensive HTTP timeout in seconds from `AGROTRACER_API_TIMEOUT` or defaults to 10s.
     *
     * @return int Timeout in seconds (clamped between 2 and 30 seconds).
     */
    public static function resolve_timeout(): int {
        if (defined('AGROTRACER_API_TIMEOUT') && is_numeric(AGROTRACER_API_TIMEOUT)) {
            $timeout = (int) AGROTRACER_API_TIMEOUT;
            return max(2, min(30, $timeout));
        }

        return self::DEFAULT_TIMEOUT_SECONDS;
    }

    /**
     * Strictly resolves and authorizes the current WordPress actor on the server.
     *
     * Rules enforced:
     * 1. Validates WordPress CSRF nonce via `wp_verify_nonce()`.
     * 2. Validates user capabilities via `current_user_can()`.
     * 3. Resolves actor ID strictly via `get_current_user_id()` (> 0).
     * 4. Never accepts or propagates `user_id` coming from request/browser parameters.
     *
     * @param string|null $wp_nonce            WordPress nonce string from header/request.
     * @param string      $nonce_action        Expected WordPress nonce action (default: `wp_rest`).
     * @param string      $required_capability Capability required for the operation.
     * @return int Authenticated and authorized WordPress user ID (> 0).
     * @throws RuntimeException With code 401 or 403 if authentication, nonce, or capability fails.
     */
    public static function resolve_authorized_actor(
        ?string $wp_nonce,
        string $nonce_action = 'wp_rest',
        string $required_capability = self::DEFAULT_REQUIRED_CAPABILITY
    ): int {
        if (!is_string($wp_nonce) || trim($wp_nonce) === '') {
            throw new RuntimeException('Sessão expirada ou token de segurança (nonce) ausente.', 401);
        }

        $nonce_valid = function_exists('wp_verify_nonce')
            ? wp_verify_nonce($wp_nonce, $nonce_action)
            : false;

        if ($nonce_valid === false || $nonce_valid === 0) {
            throw new RuntimeException('Token de segurança (nonce) inválido ou expirado. Recarregue a página.', 401);
        }

        $actor_id = function_exists('get_current_user_id') ? (int) get_current_user_id() : 0;
        if ($actor_id <= self::SYSTEM_USER_ID) {
            throw new RuntimeException('Operação restrita a usuários autenticados no WordPress.', 401);
        }

        $has_capability = function_exists('current_user_can') && (
            current_user_can($required_capability) ||
            current_user_can('publish_posts')
        );

        if (!$has_capability) {
            throw new RuntimeException('Você não possui permissão para realizar esta operação.', 403);
        }

        return $actor_id;
    }

    /**
     * Strips any untrusted actor/user identifier keys sent by the browser payload
     * and binds the server-resolved actor ID when requested.
     *
     * @param array<string, mixed> $payload           Input payload array from request.
     * @param int                  $resolved_actor_id Server-side `get_current_user_id()`.
     * @param bool                 $bind_produtor_id  Whether to inject `produtor_id = $resolved_actor_id`.
     * @return array<string, mixed> Sanitized payload free of spoofed user identifiers.
     */
    public static function sanitize_actor_payload(
        array $payload,
        int $resolved_actor_id,
        bool $bind_produtor_id = false
    ): array {
        $forbidden_keys = [
            'user_id',
            'wp_user_id',
            'wordpress_user_id',
            'actor_id',
            'x_agrotracer_actor_id',
            'x_agrotracer_user_id',
            'produtor_id',
        ];

        $sanitized = [];
        foreach ($payload as $key => $value) {
            if (!in_array(strtolower((string) $key), $forbidden_keys, true)) {
                $sanitized[$key] = $value;
            }
        }

        if ($bind_produtor_id) {
            $sanitized['produtor_id'] = $resolved_actor_id;
        }

        return $sanitized;
    }

    /**
     * Builds the mandatory signed HTTP headers for FastAPI bridge requests.
     *
     * Mandatory Headers included:
     * - `X-AgroTracer-Actor-ID`: Authenticated user ID resolved on the server.
     * - `X-AgroTracer-User-Id`: Alias maintained for ADR-002 FastAPI compatibility.
     * - `X-AgroTracer-Timestamp`: UNIX UTC timestamp of request generation.
     * - `X-AgroTracer-Nonce`: Unique cryptographic random string for anti-replay.
     * - `X-AgroTracer-Signature`: HMAC-SHA256 hex signature of the canonical payload.
     * - `X-Correlation-ID`: End-to-end distributed tracing UUIDv4.
     *
     * @param string      $method          HTTP method (`GET`, `POST`, etc.).
     * @param string      $path_with_query Relative path and query string.
     * @param string      $raw_body        Raw JSON body string (`""` for GET).
     * @param int         $actor_id        Server-resolved WordPress user ID.
     * @param string|null $correlation_id  Optional UUIDv4 correlation ID.
     * @param int|null    $timestamp       Optional UNIX UTC timestamp (defaults to `time()`).
     * @param string|null $nonce           Optional 32-char hex nonce.
     * @param string|null $secret_key      Optional HMAC secret override.
     * @return array<string, string> Associative array of signed HTTP headers.
     */
    public static function build_signed_headers(
        string $method,
        string $path_with_query,
        string $raw_body,
        int $actor_id,
        ?string $correlation_id = null,
        ?int $timestamp = null,
        ?string $nonce = null,
        ?string $secret_key = null
    ): array {
        $timestamp_utc = $timestamp ?? time();
        $nonce_hex     = $nonce ?? self::generate_nonce();
        $corr_uuid     = self::resolve_correlation_id($correlation_id);
        $resolved_key  = $secret_key ?? self::resolve_hmac_secret();

        $canonical = self::build_canonical_string(
            $method,
            $path_with_query,
            $timestamp_utc,
            $nonce_hex,
            $actor_id,
            $raw_body
        );

        $signature = self::compute_hmac_signature($canonical, $resolved_key);

        return [
            'Content-Type'           => 'application/json',
            'Accept'                 => 'application/json',
            'X-AgroTracer-Actor-ID'  => (string) $actor_id,
            'X-AgroTracer-User-Id'   => (string) $actor_id,
            'X-AgroTracer-Timestamp' => (string) $timestamp_utc,
            'X-AgroTracer-Nonce'     => $nonce_hex,
            'X-AgroTracer-Signature' => $signature,
            'X-Correlation-ID'       => $corr_uuid,
            'User-Agent'             => 'AgroTracer-Bridge/3.1.0 (WordPress)',
        ];
    }

    /**
     * Verifies an incoming or simulated signed request (used for contract verification
     * and automated security testing of tampering, timestamp skew, and replay attacks).
     *
     * @param string                     $method          HTTP method.
     * @param string                     $path_with_query Request path and query string.
     * @param string                     $raw_body        Raw request body bytes.
     * @param array<string, string|null> $headers         Request headers.
     * @param string                     $secret_key      Shared HMAC secret key.
     * @param array<string, int>         &$nonce_registry In-memory/Redis nonce store `[nonce => expires_at]` passed by reference.
     * @param int|null                   $current_time    Current UNIX UTC time (defaults to `time()`).
     * @return array{valid: bool, status: int, code: string, message: string, correlation_id: string}
     */
    public static function verify_signed_request(
        string $method,
        string $path_with_query,
        string $raw_body,
        array $headers,
        string $secret_key,
        array &$nonce_registry = [],
        ?int $current_time = null
    ): array {
        $now = $current_time ?? time();

        // Normalize header lookup case-insensitively
        $norm_headers = [];
        foreach ($headers as $k => $v) {
            $norm_headers[strtolower((string) $k)] = is_string($v) ? trim($v) : null;
        }

        $corr_id   = self::resolve_correlation_id($norm_headers['x-correlation-id'] ?? null);
        $actor_hdr = $norm_headers['x-agrotracer-actor-id'] ?? ($norm_headers['x-agrotracer-user-id'] ?? null);
        $ts_hdr    = $norm_headers['x-agrotracer-timestamp'] ?? null;
        $nonce_hdr = $norm_headers['x-agrotracer-nonce'] ?? null;
        $sig_hdr   = $norm_headers['x-agrotracer-signature'] ?? null;

        if (
            $actor_hdr === null || $actor_hdr === '' ||
            $ts_hdr === null || $ts_hdr === '' ||
            $nonce_hdr === null || $nonce_hdr === '' ||
            $sig_hdr === null || $sig_hdr === ''
        ) {
            return [
                'valid'          => false,
                'status'         => 401,
                'code'           => 'AUTH_INVALID_REQUEST',
                'message'        => self::map_error_to_ui_message(401, 'AUTH_INVALID_REQUEST'),
                'correlation_id' => $corr_id,
            ];
        }

        // If both Actor-ID and User-Id headers are present, they must be identical
        if (
            isset($norm_headers['x-agrotracer-actor-id'], $norm_headers['x-agrotracer-user-id']) &&
            $norm_headers['x-agrotracer-actor-id'] !== $norm_headers['x-agrotracer-user-id']
        ) {
            return [
                'valid'          => false,
                'status'         => 401,
                'code'           => 'AUTH_ACTOR_MISMATCH',
                'message'        => self::map_error_to_ui_message(401, 'AUTH_INVALID_REQUEST'),
                'correlation_id' => $corr_id,
            ];
        }

        if (
            preg_match('/^(0|[1-9][0-9]{0,19})$/', $actor_hdr) !== 1 ||
            preg_match('/^[0-9]{1,20}$/', $ts_hdr) !== 1 ||
            preg_match('/^[0-9a-f]{32}$/', $nonce_hdr) !== 1 ||
            preg_match('/^[0-9a-f]{64}$/', $sig_hdr) !== 1
        ) {
            return [
                'valid'          => false,
                'status'         => 401,
                'code'           => 'AUTH_INVALID_REQUEST',
                'message'        => self::map_error_to_ui_message(401, 'AUTH_INVALID_REQUEST'),
                'correlation_id' => $corr_id,
            ];
        }

        $timestamp = (int) $ts_hdr;
        $actor_id  = (int) $actor_hdr;

        // 1. Validate timestamp tolerance window (±300s)
        if (abs($now - $timestamp) > self::TIMESTAMP_TOLERANCE_SECONDS) {
            return [
                'valid'          => false,
                'status'         => 401,
                'code'           => 'AUTH_TIMESTAMP_EXPIRED',
                'message'        => self::map_error_to_ui_message(401, 'AUTH_INVALID_REQUEST'),
                'correlation_id' => $corr_id,
            ];
        }

        // 2. Compute canonical string and verify HMAC-SHA256 using constant-time hash_equals
        try {
            $canonical = self::build_canonical_string(
                $method,
                $path_with_query,
                $timestamp,
                $nonce_hdr,
                $actor_id,
                $raw_body
            );
        } catch (InvalidArgumentException $e) {
            return [
                'valid'          => false,
                'status'         => 401,
                'code'           => 'AUTH_INVALID_URI',
                'message'        => self::map_error_to_ui_message(401, 'AUTH_INVALID_REQUEST'),
                'correlation_id' => $corr_id,
            ];
        }

        $expected_sig = self::compute_hmac_signature($canonical, $secret_key);
        if (!hash_equals($expected_sig, $sig_hdr)) {
            return [
                'valid'          => false,
                'status'         => 401,
                'code'           => 'AUTH_SIGNATURE_MISMATCH',
                'message'        => self::map_error_to_ui_message(401, 'AUTH_INVALID_REQUEST'),
                'correlation_id' => $corr_id,
            ];
        }

        // 3. Anti-replay verification (purge expired nonces and reject active duplicate nonces)
        foreach ($nonce_registry as $stored_nonce => $expires_at) {
            if ($expires_at <= $now) {
                unset($nonce_registry[$stored_nonce]);
            }
        }

        if (isset($nonce_registry[$nonce_hdr])) {
            return [
                'valid'          => false,
                'status'         => 401,
                'code'           => 'AUTH_NONCE_REPLAYED',
                'message'        => self::map_error_to_ui_message(401, 'AUTH_INVALID_REQUEST'),
                'correlation_id' => $corr_id,
            ];
        }

        // Store nonce with 660s TTL (equivalent to Redis SET NX EX 660)
        $nonce_registry[$nonce_hdr] = $now + self::NONCE_TTL_SECONDS;

        return [
            'valid'          => true,
            'status'         => 200,
            'code'           => 'OK',
            'message'        => 'Requisição autenticada com sucesso.',
            'correlation_id' => $corr_id,
        ];
    }

    /**
     * Maps HTTP status codes (400, 401, 403, 404, 409, 422, 429, 500, 503) and domain error codes
     * returned by FastAPI/PostgreSQL into safe, clear, non-leaky UI messages for the end user.
     *
     * Never exposes SQL errors, Python stack traces, internal table names, or HMAC details.
     *
     * @param int                  $status_code  HTTP status code from FastAPI.
     * @param string|null          $error_code   Domain error code (e.g., `CAR_JA_CADASTRADO`).
     * @param array<string, mixed> $field_errors Optional validation field errors.
     * @return string Friendly and safe PT-BR message for the user interface.
     */
    public static function map_error_to_ui_message(
        int $status_code,
        ?string $error_code = null,
        array $field_errors = []
    ): string {
        $normalized_code = is_string($error_code) ? strtoupper(trim($error_code)) : '';

        // Domain-specific friendly messages (safe allowlist)
        $domain_messages = [
            'CAR_JA_CADASTRADO'       => 'Este número de CAR já está vinculado a outra propriedade rural.',
            'MANEJO_SOBREPOSTO'       => 'Existe sobreposição de datas com outro manejo já registrado para este lote.',
            'ANIMAL_JA_ASSOCIADO'     => 'Este animal já possui associação ativa em outro lote no período selecionado.',
            'LOTE_JA_CERTIFICADO'     => 'Este lote já possui um certificado ativo emitido.',
            'DENOMINADOR_INVALIDO'    => 'Os dados de peso ou rendimento informados são inválidos para o cálculo de emissões.',
            'AUTH_USER_REQUIRED'      => 'Esta operação exige um usuário autenticado com perfil de Produtor Rural.',
            'AUTH_INVALID_REQUEST'    => 'Não foi possível validar a autenticidade da sua sessão com o servidor. Recarregue a página e tente novamente.',
            'AUTH_SERVICE_UNAVAILABLE'=> 'O serviço de validação de segurança está temporariamente indisponível. Tente novamente em instantes.',
        ];

        if ($normalized_code !== '' && isset($domain_messages[$normalized_code])) {
            return $domain_messages[$normalized_code];
        }

        switch ($status_code) {
            case 400:
                return 'A requisição enviada possui formato inválido. Verifique os dados preenchidos e tente novamente.';

            case 401:
                return 'Não foi possível validar a autenticidade da sua sessão com o servidor. Recarregue a página e faça login novamente.';

            case 403:
                return 'Acesso negado. Você não possui permissão para visualizar ou alterar este registro.';

            case 404:
                return 'O registro solicitado não foi encontrado ou não está disponível para o seu perfil.';

            case 409:
                return 'Conflito de atualização: este registro já existe ou possui um vínculo ativo que impede a operação.';

            case 422:
                if (!empty($field_errors)) {
                    return 'Existem campos com valores inválidos ou incompletos. Revise os destaques no formulário antes de continuar.';
                }
                return 'Os dados informados não atenderam às regras de validação. Revise os campos do formulário e tente novamente.';

            case 429:
                return 'Muitas solicitações realizadas em sequência. Aguarde alguns segundos antes de tentar novamente.';

            case 500:
            case 502:
            case 503:
            case 504:
            default:
                return 'O serviço de rastreabilidade está temporariamente indisponível. Nenhuma alteração foi perdida; tente novamente em alguns instantes.';
        }
    }

    /**
     * Normalizes the raw HTTP response from `wp_remote_get` or `wp_remote_post` into a uniform,
     * sanitized structure with user-friendly UI error messages.
     *
     * @param array<string, mixed>|\WP_Error $wp_response    Response returned by `wp_remote_get`/`wp_remote_post`.
     * @param string                         $correlation_id Request correlation ID.
     * @param int                            $timestamp_utc  Request UNIX timestamp.
     * @return array{
     *     success: bool,
     *     status: int,
     *     data: mixed,
     *     error: array{code: string, message: string, field_errors: array<string, mixed>, correlation_id: string, timestamp: string}|null,
     *     correlation_id: string,
     *     timestamp: int
     * }
     */
    public static function format_api_response($wp_response, string $correlation_id, int $timestamp_utc): array {
        if (function_exists('is_wp_error') && is_wp_error($wp_response)) {
            return [
                'success'        => false,
                'status'         => 503,
                'data'           => null,
                'error'          => [
                    'code'           => 'SERVICE_UNAVAILABLE',
                    'message'        => self::map_error_to_ui_message(503),
                    'field_errors'   => [],
                    'correlation_id' => $correlation_id,
                    'timestamp'      => gmdate('Y-m-d\TH:i:s\Z', $timestamp_utc),
                ],
                'correlation_id' => $correlation_id,
                'timestamp'      => $timestamp_utc,
            ];
        }

        $status_code = function_exists('wp_remote_retrieve_response_code')
            ? (int) wp_remote_retrieve_response_code($wp_response)
            : (int) ($wp_response['response']['code'] ?? 500);

        $raw_body = function_exists('wp_remote_retrieve_body')
            ? (string) wp_remote_retrieve_body($wp_response)
            : (string) ($wp_response['body'] ?? '');

        $resp_corr_header = function_exists('wp_remote_retrieve_header')
            ? (string) wp_remote_retrieve_header($wp_response, 'x-correlation-id')
            : (string) ($wp_response['headers']['x-correlation-id'] ?? '');

        $resolved_corr_id = $resp_corr_header !== ''
            ? self::resolve_correlation_id($resp_corr_header)
            : $correlation_id;

        $decoded = $raw_body !== '' ? json_decode($raw_body, true) : null;

        if ($status_code >= 200 && $status_code < 300) {
            $payload_data = is_array($decoded) && array_key_exists('data', $decoded)
                ? $decoded['data']
                : $decoded;

            return [
                'success'        => true,
                'status'         => $status_code,
                'data'           => $payload_data,
                'error'          => null,
                'correlation_id' => $resolved_corr_id,
                'timestamp'      => $timestamp_utc,
            ];
        }

        $api_error_code = 'API_ERROR_' . $status_code;
        $field_errors   = [];

        if (is_array($decoded)) {
            if (isset($decoded['error']) && is_array($decoded['error'])) {
                if (!empty($decoded['error']['code']) && is_string($decoded['error']['code'])) {
                    $api_error_code = $decoded['error']['code'];
                }
                if (!empty($decoded['error']['field_errors']) && is_array($decoded['error']['field_errors'])) {
                    $field_errors = self::sanitize_field_errors($decoded['error']['field_errors']);
                }
            } elseif (isset($decoded['detail']) && is_array($decoded['detail'])) {
                // FastAPI default 422 Pydantic validation format fallback
                $api_error_code = 'VALIDATION_ERROR';
                foreach ($decoded['detail'] as $item) {
                    if (is_array($item) && isset($item['loc']) && is_array($item['loc'])) {
                        $field_name = (string) end($item['loc']);
                        $field_errors[$field_name] = 'Revise o valor informado neste campo.';
                    }
                }
            }
        }

        $safe_ui_message = self::map_error_to_ui_message($status_code, $api_error_code, $field_errors);

        return [
            'success'        => false,
            'status'         => $status_code,
            'data'           => null,
            'error'          => [
                'code'           => $api_error_code,
                'message'        => $safe_ui_message,
                'field_errors'   => $field_errors,
                'correlation_id' => $resolved_corr_id,
                'timestamp'      => gmdate('Y-m-d\TH:i:s\Z', $timestamp_utc),
            ],
            'correlation_id' => $resolved_corr_id,
            'timestamp'      => $timestamp_utc,
        ];
    }

    /**
     * Sanitizes field-level validation messages so internal exceptions or SQL snippets
     * are never leaked to the browser.
     *
     * @param array<string, mixed> $raw_field_errors Raw field errors dictionary.
     * @return array<string, string> Sanitized field errors.
     */
    private static function sanitize_field_errors(array $raw_field_errors): array {
        $clean = [];
        foreach ($raw_field_errors as $field => $msg) {
            $safe_field = preg_replace('/[^a-zA-Z0-9_\-\.]/', '', (string) $field) ?: 'campo';
            $msg_len    = is_string($msg) ? (function_exists('mb_strlen') ? mb_strlen($msg) : strlen($msg)) : 999;
            if (is_string($msg) && $msg_len <= 160 && stripos($msg, 'select ') === false && stripos($msg, 'traceback') === false) {
                $clean[$safe_field] = function_exists('sanitize_text_field')
                    ? sanitize_text_field($msg)
                    : strip_tags($msg);
            } else {
                $clean[$safe_field] = 'Valor inválido para este campo.';
            }
        }
        return $clean;
    }

    /**
     * Executes a signed HTTP GET request to the FastAPI backend using `wp_remote_get()`.
     *
     * @param string               $path           Relative API endpoint path (e.g., `/api/v1/fazendas`).
     * @param array<string, mixed> $query_params   Optional associative array of query string parameters.
     * @param int                  $actor_id       Authenticated WordPress user ID resolved via `get_current_user_id()`.
     * @param string|null          $correlation_id Optional UUIDv4 correlation ID.
     * @param int|null             $timeout        Optional defensive timeout in seconds.
     * @return array<string, mixed> Standardized response envelope with safe UI messages.
     */
    public static function get(
        string $path,
        array $query_params,
        int $actor_id,
        ?string $correlation_id = null,
        ?int $timeout = null
    ): array {
        $timestamp_utc = time();
        $corr_uuid     = self::resolve_correlation_id($correlation_id);

        if ($actor_id <= self::SYSTEM_USER_ID) {
            return [
                'success'        => false,
                'status'         => 403,
                'data'           => null,
                'error'          => [
                    'code'           => 'AUTH_USER_REQUIRED',
                    'message'        => self::map_error_to_ui_message(403, 'AUTH_USER_REQUIRED'),
                    'field_errors'   => [],
                    'correlation_id' => $corr_uuid,
                    'timestamp'      => gmdate('Y-m-d\TH:i:s\Z', $timestamp_utc),
                ],
                'correlation_id' => $corr_uuid,
                'timestamp'      => $timestamp_utc,
            ];
        }

        // Strip any untrusted actor/user IDs from query parameters
        $clean_query = self::sanitize_actor_payload($query_params, $actor_id, false);
        $path_with_query = $path;

        if (!empty($clean_query)) {
            $qs = http_build_query($clean_query, '', '&', PHP_QUERY_RFC3986);
            if ($qs !== '') {
                $path_with_query .= (strpos($path, '?') === false ? '?' : '&') . $qs;
            }
        }

        try {
            $normalized_uri = self::normalize_path_query($path_with_query);
            $headers = self::build_signed_headers(
                'GET',
                $normalized_uri,
                '',
                $actor_id,
                $corr_uuid,
                $timestamp_utc
            );
        } catch (\Throwable $e) {
            return [
                'success'        => false,
                'status'         => 400,
                'data'           => null,
                'error'          => [
                    'code'           => 'INVALID_REQUEST_URI',
                    'message'        => self::map_error_to_ui_message(400),
                    'field_errors'   => [],
                    'correlation_id' => $corr_uuid,
                    'timestamp'      => gmdate('Y-m-d\TH:i:s\Z', $timestamp_utc),
                ],
                'correlation_id' => $corr_uuid,
                'timestamp'      => $timestamp_utc,
            ];
        }

        $target_url = self::resolve_api_base_url() . $normalized_uri;
        $defensive_timeout = $timeout ?? self::resolve_timeout();

        $wp_response = wp_remote_get($target_url, [
            'headers'     => $headers,
            'timeout'     => $defensive_timeout,
            'redirection' => 0,
            'httpversion' => '1.1',
            'sslverify'   => self::should_verify_ssl(),
        ]);

        return self::format_api_response($wp_response, $corr_uuid, $timestamp_utc);
    }

    /**
     * Executes a signed HTTP POST request to the FastAPI backend using `wp_remote_post()`.
     *
     * @param string               $path             Relative API endpoint path (e.g., `/api/v1/fazendas`).
     * @param array<string, mixed> $body_payload     Request payload array (any spoofed `user_id` is stripped).
     * @param int                  $actor_id         Authenticated WordPress user ID resolved via `get_current_user_id()`.
     * @param string|null          $correlation_id   Optional UUIDv4 correlation ID.
     * @param bool                 $bind_produtor_id Whether to bind `produtor_id = $actor_id` in the payload.
     * @param int|null             $timeout          Optional defensive timeout in seconds.
     * @return array<string, mixed> Standardized response envelope with safe UI messages.
     */
    public static function post(
        string $path,
        array $body_payload,
        int $actor_id,
        ?string $correlation_id = null,
        bool $bind_produtor_id = true,
        ?int $timeout = null
    ): array {
        $timestamp_utc = time();
        $corr_uuid     = self::resolve_correlation_id($correlation_id);

        if ($actor_id <= self::SYSTEM_USER_ID) {
            return [
                'success'        => false,
                'status'         => 403,
                'data'           => null,
                'error'          => [
                    'code'           => 'AUTH_USER_REQUIRED',
                    'message'        => self::map_error_to_ui_message(403, 'AUTH_USER_REQUIRED'),
                    'field_errors'   => [],
                    'correlation_id' => $corr_uuid,
                    'timestamp'      => gmdate('Y-m-d\TH:i:s\Z', $timestamp_utc),
                ],
                'correlation_id' => $corr_uuid,
                'timestamp'      => $timestamp_utc,
            ];
        }

        // Enforce strict server-side identity: strip any browser-supplied user_id/actor_id
        $sanitized_payload = self::sanitize_actor_payload($body_payload, $actor_id, $bind_produtor_id);

        $raw_body = function_exists('wp_json_encode')
            ? (string) wp_json_encode($sanitized_payload)
            : (string) json_encode($sanitized_payload, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);

        try {
            $normalized_uri = self::normalize_path_query($path);
            $headers = self::build_signed_headers(
                'POST',
                $normalized_uri,
                $raw_body,
                $actor_id,
                $corr_uuid,
                $timestamp_utc
            );
        } catch (\Throwable $e) {
            return [
                'success'        => false,
                'status'         => 400,
                'data'           => null,
                'error'          => [
                    'code'           => 'INVALID_REQUEST_URI',
                    'message'        => self::map_error_to_ui_message(400),
                    'field_errors'   => [],
                    'correlation_id' => $corr_uuid,
                    'timestamp'      => gmdate('Y-m-d\TH:i:s\Z', $timestamp_utc),
                ],
                'correlation_id' => $corr_uuid,
                'timestamp'      => $timestamp_utc,
            ];
        }

        $target_url = self::resolve_api_base_url() . $normalized_uri;
        $defensive_timeout = $timeout ?? self::resolve_timeout();

        $wp_response = wp_remote_post($target_url, [
            'headers'     => $headers,
            'body'        => $raw_body,
            'timeout'     => $defensive_timeout,
            'redirection' => 0,
            'httpversion' => '1.1',
            'data_format' => 'body',
            'sslverify'   => self::should_verify_ssl(),
        ]);

        return self::format_api_response($wp_response, $corr_uuid, $timestamp_utc);
    }

    /**
     * Determines whether TLS certificate verification should be enforced.
     * Enabled by default in staging/production; configurable via `AGROTRACER_API_SSLVERIFY`.
     *
     * @return bool True to verify SSL certificates.
     */
    private static function should_verify_ssl(): bool {
        if (defined('AGROTRACER_API_SSLVERIFY')) {
            return (bool) AGROTRACER_API_SSLVERIFY;
        }

        $app_env = defined('WP_ENVIRONMENT_TYPE') ? (string) WP_ENVIRONMENT_TYPE : (string) getenv('APP_ENV');
        return in_array($app_env, ['production', 'staging'], true);
    }
}
