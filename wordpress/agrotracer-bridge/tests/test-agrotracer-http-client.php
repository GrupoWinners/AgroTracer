<?php
/**
 * Automated Unit & Integration Test Suite for AgroTracer_Http_Client
 *
 * Covers Epic [EP-S1] Sprint 1 — Data & Identity Foundation (Task S1-T04 / ADR-002):
 * 1. Happy Path: Valid GET and POST requests with mandatory signed headers, RFC 3986
 *    query normalization, defensive timeout, and 100% parity with Python FastAPI HMAC vectors.
 * 2. Tampering Rejection (HTTP 401):
 *    - Spoofed/tampered `user_id` (`X-AgroTracer-Actor-ID` / `X-AgroTracer-User-Id`).
 *    - Request body modified after HMAC signature computation.
 *    - Timestamp outside the ±300s tolerance window (expired or future clock skew).
 *    - Replayed nonce within the 660s retention window (anti-replay protection).
 * 3. Server-Side Identity & Non-Leaky UI Error Mapping (400, 401, 403, 404, 409, 422, 500).
 *
 * @package AgroTracerBridge\Tests
 */

declare(strict_types=1);

namespace AgroTracerBridge\Tests;

require_once __DIR__ . '/bootstrap.php';

use AgroTracerBridge\Http\AgroTracer_Http_Client;
use AgroTracer_WP_Test_Mock_State;
use PHPUnit\Framework\TestCase;
use RuntimeException;

/**
 * Class AgroTracerHttpClientTest
 */
class AgroTracerHttpClientTest extends TestCase {

    private string $shared_secret = 'agrotracer_chave_exclusivamente_teste_2026';

    protected function setUp(): void {
        parent::setUp();
        AgroTracer_WP_Test_Mock_State::reset();
    }

    /**
     * [AC-01 / Happy Path GET]
     * Verifies that a GET request with query parameters generates valid mandatory headers,
     * normalizes the query string per RFC 3986, enforces defensive timeout, and passes
     * backend HMAC verification (HTTP 200 OK).
     */
    public function test_happy_path_get_request_with_valid_headers_and_signature_is_approved(): void {
        $nonce_registry = [];
        $actor_id = AgroTracer_Http_Client::resolve_authorized_actor('valid_wp_nonce_token_123', 'wp_rest');
        $this->assertSame(42, $actor_id);

        AgroTracer_WP_Test_Mock_State::$remote_handler = function (string $url, array $args) use (&$nonce_registry): array {
            $parsed = parse_url($url);
            $path_with_query = ($parsed['path'] ?? '/') . (isset($parsed['query']) ? '?' . $parsed['query'] : '');

            $verification = AgroTracer_Http_Client::verify_signed_request(
                'GET',
                $path_with_query,
                '',
                $args['headers'],
                $this->shared_secret,
                $nonce_registry
            );

            $this->assertTrue($verification['valid'], 'FastAPI simulator must approve valid GET signature.');
            $this->assertSame(200, $verification['status']);

            return [
                'response' => ['code' => 200, 'message' => 'OK'],
                'headers'  => ['x-correlation-id' => $args['headers']['X-Correlation-ID']],
                'body'     => json_encode([
                    'data' => [
                        ['id' => 1, 'nome_propriedade' => 'Fazenda Modelo', 'uf' => 'MS'],
                    ],
                ]),
            ];
        };

        $response = AgroTracer_Http_Client::get(
            '/api/v1/fazendas',
            ['uf' => 'MS', 'nome' => 'Fazenda Modelo', 'user_id' => 999], // spoofed user_id must be stripped
            $actor_id,
            'f2079c68-fbe4-4d92-9fb4-55daba0c666b',
            10
        );

        $this->assertTrue($response['success']);
        $this->assertSame(200, $response['status']);
        $this->assertSame('f2079c68-fbe4-4d92-9fb4-55daba0c666b', $response['correlation_id']);
        $this->assertSame('Fazenda Modelo', $response['data'][0]['nome_propriedade']);

        // Inspect dispatched wp_remote_get call
        $dispatched = AgroTracer_WP_Test_Mock_State::$dispatched_requests[0];
        $this->assertSame('http://127.0.0.1:8000/api/v1/fazendas?nome=Fazenda%20Modelo&uf=MS', $dispatched['url']);
        $this->assertSame(10, $dispatched['args']['timeout']);

        $headers = $dispatched['args']['headers'];
        $this->assertSame('42', $headers['X-AgroTracer-Actor-ID']);
        $this->assertSame('42', $headers['X-AgroTracer-User-Id']);
        $this->assertMatchesRegularExpression('/^[0-9a-f]{32}$/', $headers['X-AgroTracer-Nonce']);
        $this->assertMatchesRegularExpression('/^[0-9a-f]{64}$/', $headers['X-AgroTracer-Signature']);
        $this->assertSame('f2079c68-fbe4-4d92-9fb4-55daba0c666b', $headers['X-Correlation-ID']);
    }

    /**
     * [AC-01 / Happy Path POST + Official Cross-Runtime Vector Match]
     * Verifies that a POST request with JSON payload computes the exact HMAC-SHA256
     * signature, strips any browser-supplied `user_id`, binds the server-resolved `actor_id`,
     * and matches the official Python/PHP test vector (`S0-T06`).
     */
    public function test_happy_path_post_request_and_official_vector_match(): void {
        // 1. Validate exact parity with Official Test Vector #1 (S0-T06)
        $canonical_v1 = AgroTracer_Http_Client::build_canonical_string(
            'POST',
            '/api/v1/fazendas',
            1792020000,
            '00112233445566778899aabbccddeeff',
            42,
            '{}'
        );
        $sig_v1 = AgroTracer_Http_Client::compute_hmac_signature($canonical_v1, $this->shared_secret);
        $this->assertSame(
            'ca62dbbd01854e311b419ff2e64d3721e0ccb6bf698ebcf94f9026e5d562c9bc',
            $sig_v1,
            'Must match 100% with Python FastAPI hmac_protocol.py official vector #1'
        );

        // 2. Validate end-to-end POST via wp_remote_post
        $nonce_registry = [];
        AgroTracer_WP_Test_Mock_State::$remote_handler = function (string $url, array $args) use (&$nonce_registry): array {
            $parsed = parse_url($url);
            $verification = AgroTracer_Http_Client::verify_signed_request(
                'POST',
                $parsed['path'] ?? '/api/v1/fazendas',
                (string) $args['body'],
                $args['headers'],
                $this->shared_secret,
                $nonce_registry
            );

            $this->assertTrue($verification['valid']);
            $decoded_body = json_decode((string) $args['body'], true);

            // Verify that spoofed user_id=777 was stripped and produtor_id=42 was bound server-side
            $this->assertArrayNotHasKey('user_id', $decoded_body);
            $this->assertSame(42, $decoded_body['produtor_id']);

            return [
                'response' => ['code' => 201, 'message' => 'Created'],
                'headers'  => ['x-correlation-id' => $args['headers']['X-Correlation-ID']],
                'body'     => json_encode([
                    'data' => [
                        'id'               => 10,
                        'nome_propriedade' => $decoded_body['nome_propriedade'],
                        'produtor_id'      => $decoded_body['produtor_id'],
                    ],
                ]),
            ];
        };

        $response = AgroTracer_Http_Client::post(
            '/api/v1/fazendas',
            [
                'nome_propriedade' => 'Fazenda Santa Clara',
                'numero_car'       => 'MG-3103504-1111.2222.3333.4444.5555.6666',
                'municipio'        => 'Araguari',
                'uf'               => 'MG',
                'user_id'          => 777, // Attempted browser spoofing
                'actor_id'         => 888, // Attempted browser spoofing
            ],
            42,
            '8d7c3f2a-9e4b-4c1a-8b2d-112233445566'
        );

        $this->assertTrue($response['success']);
        $this->assertSame(201, $response['status']);
        $this->assertSame(42, $response['data']['produtor_id']);
    }

    /**
     * [AC-02.1 / Tampering Rejection: Adulterated Actor/User ID]
     * Fails with HTTP 401 when `X-AgroTracer-Actor-ID` or `X-AgroTracer-User-Id` is modified
     * after the request is signed (BOLA/IDOR spoofing attempt).
     */
    public function test_rejection_when_actor_id_in_header_is_tampered(): void {
        $nonce_registry = [];
        $now = 1792020000;
        $raw_body = '{"nome_propriedade":"Fazenda Modelo","produtor_id":42}';

        $headers = AgroTracer_Http_Client::build_signed_headers(
            'POST',
            '/api/v1/fazendas',
            $raw_body,
            42,
            '123e4567-e89b-42d3-a456-426614174000',
            $now,
            '00112233445566778899aabbccddeeff',
            $this->shared_secret
        );

        // Attacker tampers with the Actor ID header from 42 to 99
        $headers['X-AgroTracer-Actor-ID'] = '99';
        $headers['X-AgroTracer-User-Id']  = '99';

        $verification = AgroTracer_Http_Client::verify_signed_request(
            'POST',
            '/api/v1/fazendas',
            $raw_body,
            $headers,
            $this->shared_secret,
            $nonce_registry,
            $now
        );

        $this->assertFalse($verification['valid']);
        $this->assertSame(401, $verification['status']);
        $this->assertSame('AUTH_SIGNATURE_MISMATCH', $verification['code']);
    }

    /**
     * [AC-02.2 / Tampering Rejection: Modified Request Body After Signature]
     * Fails with HTTP 401 when the JSON payload is altered in transit after HMAC signing.
     */
    public function test_rejection_when_request_body_is_modified_after_signing(): void {
        $nonce_registry = [];
        $now = 1792020000;
        $original_body = '{"nome_propriedade":"Fazenda Modelo","produtor_id":42}';
        $tampered_body = '{"nome_propriedade":"Fazenda Adulterada","produtor_id":99}';

        $headers = AgroTracer_Http_Client::build_signed_headers(
            'POST',
            '/api/v1/fazendas',
            $original_body,
            42,
            '123e4567-e89b-42d3-a456-426614174000',
            $now,
            'aabbccddeeff00112233445566778899',
            $this->shared_secret
        );

        $verification = AgroTracer_Http_Client::verify_signed_request(
            'POST',
            '/api/v1/fazendas',
            $tampered_body,
            $headers,
            $this->shared_secret,
            $nonce_registry,
            $now
        );

        $this->assertFalse($verification['valid']);
        $this->assertSame(401, $verification['status']);
        $this->assertSame('AUTH_SIGNATURE_MISMATCH', $verification['code']);
    }

    /**
     * [AC-02.3 / Tampering Rejection: Expired Timestamp Outside Tolerance Window]
     * Fails with HTTP 401 when `X-AgroTracer-Timestamp` exceeds the ±300s tolerance window.
     */
    public function test_rejection_when_timestamp_is_outside_tolerance_window(): void {
        $nonce_registry = [];
        $server_now = 1792020000;
        $expired_timestamp = $server_now - 301; // 301s old (> 300s max skew)
        $future_timestamp  = $server_now + 301; // 301s in the future (> 300s max skew)

        // Case A: Expired past timestamp (-301s)
        $headers_expired = AgroTracer_Http_Client::build_signed_headers(
            'GET',
            '/api/v1/fazendas',
            '',
            42,
            '123e4567-e89b-42d3-a456-426614174000',
            $expired_timestamp,
            '11112222333344445555666677778888',
            $this->shared_secret
        );

        $res_expired = AgroTracer_Http_Client::verify_signed_request(
            'GET',
            '/api/v1/fazendas',
            '',
            $headers_expired,
            $this->shared_secret,
            $nonce_registry,
            $server_now
        );

        $this->assertFalse($res_expired['valid']);
        $this->assertSame(401, $res_expired['status']);
        $this->assertSame('AUTH_TIMESTAMP_EXPIRED', $res_expired['code']);

        // Case B: Future skewed timestamp (+301s)
        $headers_future = AgroTracer_Http_Client::build_signed_headers(
            'GET',
            '/api/v1/fazendas',
            '',
            42,
            '123e4567-e89b-42d3-a456-426614174000',
            $future_timestamp,
            '99998888777766665555444433332222',
            $this->shared_secret
        );

        $res_future = AgroTracer_Http_Client::verify_signed_request(
            'GET',
            '/api/v1/fazendas',
            '',
            $headers_future,
            $this->shared_secret,
            $nonce_registry,
            $server_now
        );

        $this->assertFalse($res_future['valid']);
        $this->assertSame(401, $res_future['status']);
        $this->assertSame('AUTH_TIMESTAMP_EXPIRED', $res_future['code']);
    }

    /**
     * [AC-02.4 / Tampering Rejection: Nonce Replay Attack]
     * Fails with HTTP 401 when a valid signed request is re-sent using an already consumed
     * `X-AgroTracer-Nonce` within the 660-second retention TTL.
     */
    public function test_rejection_when_nonce_is_reused_in_replay_attack(): void {
        $nonce_registry = [];
        $now = 1792020000;
        $raw_body = '{"nome_propriedade":"Fazenda Modelo"}';

        $headers = AgroTracer_Http_Client::build_signed_headers(
            'POST',
            '/api/v1/fazendas',
            $raw_body,
            42,
            '123e4567-e89b-42d3-a456-426614174000',
            $now,
            'deadbeef00112233445566778899aabb',
            $this->shared_secret
        );

        // 1st attempt: Accepted (HTTP 200) and stores nonce in registry with TTL = 660s
        $first_attempt = AgroTracer_Http_Client::verify_signed_request(
            'POST',
            '/api/v1/fazendas',
            $raw_body,
            $headers,
            $this->shared_secret,
            $nonce_registry,
            $now
        );
        $this->assertTrue($first_attempt['valid']);
        $this->assertSame(200, $first_attempt['status']);

        // 2nd attempt (Replay Attack 5 seconds later with exact same valid headers & signature): Rejected (HTTP 401)
        $replay_attempt = AgroTracer_Http_Client::verify_signed_request(
            'POST',
            '/api/v1/fazendas',
            $raw_body,
            $headers,
            $this->shared_secret,
            $nonce_registry,
            $now + 5
        );
        $this->assertFalse($replay_attempt['valid']);
        $this->assertSame(401, $replay_attempt['status']);
        $this->assertSame('AUTH_NONCE_REPLAYED', $replay_attempt['code']);
    }

    /**
     * [AC-03 / Identity & Authorization Guard]
     * Verifies that `resolve_authorized_actor` rejects invalid WordPress nonces (401),
     * unauthenticated users (401), and users lacking `agrotracer_manage_farms` capability (403).
     */
    public function test_identity_and_capability_enforcement(): void {
        // 1. Invalid CSRF Nonce -> HTTP 401
        $caught_code = 0;
        try {
            AgroTracer_Http_Client::resolve_authorized_actor('forged_nonce_token', 'wp_rest');
        } catch (RuntimeException $e) {
            $caught_code = $e->getCode();
        }
        $this->assertSame(401, $caught_code, 'Invalid WP nonce must throw 401.');

        // 2. Unauthenticated user (ID = 0) -> HTTP 401
        AgroTracer_WP_Test_Mock_State::$current_user_id = 0;
        $caught_code = 0;
        try {
            AgroTracer_Http_Client::resolve_authorized_actor('valid_wp_nonce_token_123', 'wp_rest');
        } catch (RuntimeException $e) {
            $caught_code = $e->getCode();
        }
        $this->assertSame(401, $caught_code, 'Unauthenticated user (ID 0) must throw 401.');

        // 3. Authenticated user without required capability -> HTTP 403
        AgroTracer_WP_Test_Mock_State::$current_user_id = 42;
        AgroTracer_WP_Test_Mock_State::$capabilities = [];
        $caught_code = 0;
        try {
            AgroTracer_Http_Client::resolve_authorized_actor('valid_wp_nonce_token_123', 'wp_rest');
        } catch (RuntimeException $e) {
            $caught_code = $e->getCode();
        }
        $this->assertSame(403, $caught_code, 'User without capability must throw 403.');
    }

    /**
     * [AC-04 / UI Error Mapping & Zero Internal Leakage]
     * Verifies that FastAPI/PostgreSQL error codes (400, 401, 403, 404, 422, 500) are mapped
     * to clear, user-friendly PT-BR messages without leaking stack traces or SQL details.
     */
    public function test_ui_error_mapping_for_400_401_403_404_422_500_without_leaking_internals(): void {
        $status_codes = [400, 401, 403, 404, 422, 500];

        foreach ($status_codes as $status) {
            $simulated_wp_response = [
                'response' => ['code' => $status, 'message' => 'Error'],
                'headers'  => ['x-correlation-id' => '123e4567-e89b-42d3-a456-426614174000'],
                'body'     => json_encode([
                    'error' => [
                        'code'         => 'INTERNAL_DB_ERR_' . $status,
                        'message'      => 'psycopg.OperationalError: SELECT * FROM fazendas WHERE secret_key = "leak" Traceback (most recent call last)',
                        'field_errors' => $status === 422 ? ['numero_car' => 'SELECT * FROM secretos'] : [],
                    ],
                ]),
            ];

            $formatted = AgroTracer_Http_Client::format_api_response(
                $simulated_wp_response,
                '123e4567-e89b-42d3-a456-426614174000',
                1792020000
            );

            $this->assertFalse($formatted['success']);
            $this->assertSame($status, $formatted['status']);
            $ui_msg = $formatted['error']['message'];

            // Ensure no internal database or stack trace details leak to the UI message
            $this->assertStringNotContainsString('psycopg', $ui_msg);
            $this->assertStringNotContainsString('SELECT *', $ui_msg);
            $this->assertStringNotContainsString('Traceback', $ui_msg);

            if ($status === 422) {
                $this->assertSame(
                    'Valor inválido para este campo.',
                    $formatted['error']['field_errors']['numero_car'],
                    'Suspicious SQL in field_errors must be sanitized.'
                );
            }
        }
    }
}

/**
 * Direct CLI Test Runner (executes automatically when invoked via `php tests/test-agrotracer-http-client.php`)
 */
if (PHP_SAPI === 'cli' && isset($_SERVER['SCRIPT_FILENAME']) && realpath($_SERVER['SCRIPT_FILENAME']) === __FILE__) {
    $suite = new AgroTracerHttpClientTest();
    $methods = get_class_methods($suite);
    $test_methods = array_values(array_filter($methods, static fn(string $m): bool => strpos($m, 'test_') === 0));

    echo "PHPUnit / AgroTracer Bridge Security & Contract Test Runner (PHP " . PHP_VERSION . ")\n";
    echo "=========================================================================\n";

    $passed = 0;
    $failed = 0;
    $start_time = microtime(true);

    foreach ($test_methods as $method) {
        try {
            $ref_setup = new \ReflectionMethod($suite, 'setUp');
            $ref_setup->setAccessible(true);
            $ref_setup->invoke($suite);

            $suite->{$method}();
            $passed++;
            echo sprintf(" [PASS] %s\n", $method);
        } catch (\Throwable $e) {
            $failed++;
            echo sprintf(" [FAIL] %s: %s\n", $method, $e->getMessage());
        }
    }

    $elapsed_ms = round((microtime(true) - $start_time) * 1000, 2);
    echo "-------------------------------------------------------------------------\n";
    echo sprintf(
        "Time: %s ms | Tests: %d | Passed: %d | Failed: %d | Assertions: %d\n",
        $elapsed_ms,
        count($test_methods),
        $passed,
        $failed,
        TestCase::$assertion_count
    );

    exit($failed > 0 ? 1 : 0);
}
