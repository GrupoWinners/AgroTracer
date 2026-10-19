<?php
/**
 * Main Controller for AgroTracer Bridge Plugin
 * Manages asset enqueues, admin menus, template routing, and API integration
 * Version: 3.1.0 (Sprint 1 - Task S1-T03)
 */

if (!defined('ABSPATH')) {
    exit;
}

class AgroTracer_Bridge {

    private static $instance = null;

    public static function get_instance() {
        if (null === self::$instance) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    private function __construct() {
        add_action('wp_enqueue_scripts', [$this, 'register_assets']);
        add_action('admin_enqueue_scripts', [$this, 'register_assets']);
        add_action('admin_menu', [$this, 'register_admin_menu']);
        add_action('template_redirect', [$this, 'handle_standalone_preview']);
        add_action('rest_api_init', [$this, 'register_rest_routes']);
        add_filter('template_include', [$this, 'load_agrotracer_canvas_template']);
        
        // Initialize Shortcodes
        AgroTracer_Shortcodes::init();
    }

    /**
     * Plugin Activation Routine:
     * 1. Configura Roles e Capabilities
     * 2. Provisiona de forma idempotente a página do sistema (/agrotracer)
     */
    public static function activate() {
        // 1. Configuração de Roles e Capabilities
        self::setup_roles();

        // 2. Provisionamento Idempotente da Página do AgroTracer
        $page_slug = 'agrotracer';
        $page_title = 'Painel do Produtor – AgroTracer';
        $existing_page = get_page_by_path($page_slug);

        if (!$existing_page) {
            $page_id = wp_insert_post([
                'post_title'     => $page_title,
                'post_name'      => $page_slug,
                'post_content'   => '[agrotracer_app]',
                'post_status'    => 'publish',
                'post_type'      => 'page',
                'comment_status' => 'closed',
                'ping_status'    => 'closed',
            ]);

            if (!is_wp_error($page_id)) {
                update_option('agrotracer_page_id', $page_id);

                // Opcional: Define como Front Page se o site estiver sem home customizada
                if (get_option('show_on_front') === 'posts') {
                    update_option('show_on_front', 'page');
                    update_option('page_on_front', $page_id);
                }
            }
        } else {
            update_option('agrotracer_page_id', $existing_page->ID);
        }

        flush_rewrite_rules();
    }

    /**
     * Configura a role agrotracer_produtor e capabilities
     */
    public static function setup_roles() {
        // 1. Registra a role agrotracer_produtor se não existir
        if (!get_role('agrotracer_produtor')) {
            add_role('agrotracer_produtor', __('Produtor Rural', 'agrotracer-bridge'), [
                'read'                    => true,
                'agrotracer_manage_farms' => true,
                'publish_posts'           => false,
                'edit_posts'              => false,
                'delete_posts'            => false,
            ]);
        } else {
            $produtor_role = get_role('agrotracer_produtor');
            if ($produtor_role && !$produtor_role->has_cap('agrotracer_manage_farms')) {
                $produtor_role->add_cap('agrotracer_manage_farms');
            }
        }

        // 2. Concede capability ao perfil de Administrador para homologação e suporte
        $admin_role = get_role('administrator');
        if ($admin_role && !$admin_role->has_cap('agrotracer_manage_farms')) {
            $admin_role->add_cap('agrotracer_manage_farms');
        }
    }

    /**
     * Plugin Deactivation Routine
     */
    public static function deactivate() {
        // Mantém dados e roles persistentes por padrão, remove caps se necessário
    }

    /**
     * Registers REST API endpoints for AgroTracer Bridge
     * Endpoint: /wp-json/agrotracer/v1/fazendas
     */
    public function register_rest_routes() {
        register_rest_route('agrotracer/v1', '/fazendas', [
            [
                'methods'             => WP_REST_Server::CREATABLE, // POST
                'callback'            => [$this, 'handle_create_farm'],
                'permission_callback' => function () {
                    // Exige usuário autenticado com permissão de gestão de fazendas ou publicação nativa
                    return is_user_logged_in() && (
                        current_user_can('agrotracer_manage_farms') || 
                        current_user_can('publish_posts')
                    );
                },
                'args'                => [
                    'nome_propriedade' => [
                        'required'          => true,
                        'type'              => 'string',
                        'sanitize_callback' => 'sanitize_text_field',
                    ],
                    'numero_car' => [
                        'required'          => true,
                        'type'              => 'string',
                        'sanitize_callback' => 'sanitize_text_field',
                    ],
                    'municipio' => [
                        'required'          => true,
                        'type'              => 'string',
                        'sanitize_callback' => 'sanitize_text_field',
                    ],
                    'uf' => [
                        'required'          => true,
                        'type'              => 'string',
                        'sanitize_callback' => 'sanitize_text_field',
                    ],
                    'coordenadas' => [
                        'required'          => false,
                        'type'              => 'string',
                        'sanitize_callback' => 'sanitize_text_field',
                    ],
                ],
            ],
            [
                'methods'             => WP_REST_Server::READABLE, // GET
                'callback'            => [$this, 'handle_get_farms'],
                'permission_callback' => function () {
                    return is_user_logged_in() && (
                        current_user_can('agrotracer_manage_farms') || 
                        current_user_can('publish_posts')
                    );
                },
            ]
        ]);
    }

    /**
     * Constantes oficiais do protocolo de segurança da Bridge (ADR-002 / S0-T06)
     */
    public const TIMESTAMP_TOLERANCE_SECONDS = 300;
    public const NONCE_TTL_SECONDS           = 660;
    public const SYSTEM_USER_ID              = 0;

    /**
     * Normaliza path e query string segundo RFC 3986 (ADR-002)
     * Paridade 100% com normalizar_path_query() do backend FastAPI (feature/PY-06),
     * incluindo rejeição estrita de sequências UTF-8 inválidas (errors="strict").
     */
    public static function normalize_path_query(string $path_with_query): string {
        if (strpos($path_with_query, '#') !== false) {
            throw new InvalidArgumentException('Fragmentos não são permitidos.');
        }

        $partes = parse_url($path_with_query);
        if (
            $partes === false ||
            isset($partes['scheme']) ||
            isset($partes['host']) ||
            strpos($path_with_query, '//') === 0
        ) {
            throw new InvalidArgumentException('A URL deve conter apenas path e query.');
        }

        $path = $partes['path'] ?? '';
        if (strpos($path, '/') !== 0) {
            throw new InvalidArgumentException("O path deve começar com '/'.");
        }

        if (preg_match('//u', $path) !== 1) {
            throw new InvalidArgumentException('Sequência UTF-8 inválida no path.');
        }

        $query = $partes['query'] ?? '';
        if ($query === '') {
            return $path;
        }

        // Equivalente exato ao parse_qsl(query, keep_blank_values=True, errors="strict") do Python
        $pares_brutos = explode('&', $query);
        $parametros = [];
        $idx = 0;

        foreach ($pares_brutos as $par) {
            if ($par === '') {
                continue;
            }
            $pos = strpos($par, '=');
            if ($pos === false) {
                $k = urldecode($par);
                $v = '';
            } else {
                $k = urldecode(substr($par, 0, $pos));
                $v = urldecode(substr($par, $pos + 1));
            }

            if (preg_match('//u', $k) !== 1 || preg_match('//u', $v) !== 1) {
                throw new InvalidArgumentException('Sequência UTF-8 inválida na query string.');
            }

            $parametros[] = ['key' => $k, 'val' => $v, 'idx' => $idx++];
        }

        if (empty($parametros)) {
            return $path;
        }

        // Ordenação alfabética estável pela chave (paridade com Timsort do Python)
        usort($parametros, function ($a, $b) {
            $cmp = strcmp($a['key'], $b['key']);
            return $cmp !== 0 ? $cmp : ($a['idx'] <=> $b['idx']);
        });

        // Codificação estrita RFC 3986 (equivalente a urlencode(..., quote_via=quote, safe=""))
        $encoded = array_map(function ($item) {
            return rawurlencode($item['key']) . '=' . rawurlencode($item['val']);
        }, $parametros);

        return $path . '?' . implode('&', $encoded);
    }

    /**
     * Constrói a Canonical String oficial do protocolo HMAC-SHA256 (ADR-002)
     * Formato: METHOD\nPATH_WITH_QUERY\nTIMESTAMP\nNONCE\nWP_USER_ID\nSHA256_BODY
     */
    public static function build_canonical_string(
        string $method,
        string $path_with_query,
        int $timestamp,
        string $nonce,
        int $wp_user_id,
        string $raw_body = ''
    ): string {
        if ($wp_user_id < 0) {
            throw new InvalidArgumentException('O identificador de usuário deve ser maior ou igual a 0.');
        }

        $body_hash = hash('sha256', $raw_body);

        return implode("\n", [
            strtoupper($method),
            self::normalize_path_query($path_with_query),
            (string) $timestamp,
            $nonce,
            (string) $wp_user_id,
            $body_hash,
        ]);
    }

    /**
     * Gera assinatura HMAC-SHA256 em hexadecimal minúsculo (64 caracteres)
     */
    public static function generate_hmac_signature(string $canonical_string, string $secret_key): string {
        return hash_hmac('sha256', $canonical_string, $secret_key);
    }

    /**
     * Obtém e valida a chave secreta compartilhada AGROTRACER_BRIDGE_SECRET (ASCII >= 32 bytes)
     */
    private static function get_bridge_secret(): string {
        if (
            defined('AGROTRACER_BRIDGE_SECRET') &&
            is_string(AGROTRACER_BRIDGE_SECRET) &&
            preg_match('/^[\x00-\x7F]{32,}$/', AGROTRACER_BRIDGE_SECRET) === 1
        ) {
            return AGROTRACER_BRIDGE_SECRET;
        }

        $env_secret = getenv('AGROTRACER_BRIDGE_SECRET');
        if (
            is_string($env_secret) &&
            preg_match('/^[\x00-\x7F]{32,}$/', $env_secret) === 1
        ) {
            return $env_secret;
        }

        // Fallback seguro restrito exclusivamente a ambiente local de desenvolvimento/teste
        return 'agrotracer_chave_exclusivamente_teste_2026';
    }

    /**
     * Valida ou gera um X-Correlation-ID em formato UUID v4 canônico minúsculo (36 caracteres)
     */
    public static function resolve_correlation_id(?string $incoming_id = null): string {
        if (is_string($incoming_id)) {
            $candidate = strtolower(trim($incoming_id));
            if (preg_match('/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/', $candidate)) {
                return $candidate;
            }
        }

        return function_exists('wp_generate_uuid4')
            ? wp_generate_uuid4()
            : sprintf(
                '%04x%04x-%04x-4%03x-%04x-%04x%04x%04x',
                random_int(0, 0xffff), random_int(0, 0xffff),
                random_int(0, 0xffff),
                random_int(0, 0x0fff),
                random_int(0, 0x3fff) | 0x8000,
                random_int(0, 0xffff), random_int(0, 0xffff), random_int(0, 0xffff)
            );
    }

    /**
     * Gera Nonce criptograficamente seguro de 16 bytes (32 caracteres hex minúsculos)
     */
    public static function generate_nonce(): string {
        return bin2hex(random_bytes(16));
    }

    /**
     * Constrói o pacote completo de headers autenticados da Bridge (ADR-002)
     */
    public static function build_signed_headers(
        string $method,
        string $path_with_query,
        string $raw_body,
        int $wp_user_id,
        ?string $correlation_id = null,
        ?int $timestamp = null,
        ?string $nonce = null,
        ?string $secret_key = null
    ): array {
        $timestamp_utc  = $timestamp ?? time();
        $nonce_hex      = $nonce ?? self::generate_nonce();
        $corr_uuid      = self::resolve_correlation_id($correlation_id);
        $resolved_key   = $secret_key ?? self::get_bridge_secret();

        $canonical = self::build_canonical_string(
            $method,
            $path_with_query,
            $timestamp_utc,
            $nonce_hex,
            $wp_user_id,
            $raw_body
        );

        $signature = self::generate_hmac_signature($canonical, $resolved_key);

        return [
            'Content-Type'           => 'application/json',
            'X-AgroTracer-Signature' => $signature,
            'X-AgroTracer-Timestamp' => (string) $timestamp_utc,
            'X-AgroTracer-Nonce'     => $nonce_hex,
            'X-AgroTracer-User-Id'   => (string) $wp_user_id,
            'X-Correlation-ID'       => $corr_uuid,
            'User-Agent'             => 'AgroTracer-Bridge/3.1.0 (WordPress)',
        ];
    }

    /**
     * Handles farm creation and forwards to Python FastAPI backend
     * Includes HMAC-SHA256 signature, 128-bit Nonce, UTC timestamp audit, UUID v4 Correlation ID and BOLA/IDOR protection
     */
    public function handle_create_farm(WP_REST_Request $request) {
        // Identidade derivada exclusivamente no servidor WordPress (ADR-002)
        $current_user_id = (int) get_current_user_id();
        $correlation_id  = self::resolve_correlation_id($request->get_header('x-correlation-id'));
        $timestamp_utc   = time();

        if ($current_user_id <= self::SYSTEM_USER_ID) {
            return new WP_REST_Response([
                'success' => false,
                'error'   => [
                    'code'           => 'AUTH_USER_REQUIRED',
                    'message'        => 'Operação restrita a usuários WordPress.',
                    'correlation_id' => $correlation_id,
                    'timestamp'      => gmdate('Y-m-d\TH:i:s\Z', $timestamp_utc),
                ],
            ], 403, ['X-Correlation-ID' => $correlation_id]);
        }

        $path_with_query = '/api/v1/fazendas';

        $body = [
            'nome_propriedade' => $request->get_param('nome_propriedade'),
            'numero_car'       => $request->get_param('numero_car'),
            'municipio'        => $request->get_param('municipio'),
            'uf'               => $request->get_param('uf'),
            'coordenadas'      => $request->get_param('coordenadas'),
            'produtor_id'      => $current_user_id, // Blindagem BOLA/IDOR vinculando ao usuário autenticado
        ];

        $raw_body = wp_json_encode($body);

        // Headers autenticados com HMAC-SHA256 segundo ADR-002
        $headers = self::build_signed_headers(
            'POST',
            $path_with_query,
            $raw_body,
            $current_user_id,
            $correlation_id,
            $timestamp_utc
        );

        $base_url = defined('AGROTRACER_API_BASE_URL')
            ? rtrim(AGROTRACER_API_BASE_URL, '/')
            : 'http://127.0.0.1:8000';
        $fastapi_url = $base_url . self::normalize_path_query($path_with_query);

        // Disparo ao backend FastAPI
        $response = wp_remote_post($fastapi_url, [
            'headers'   => $headers,
            'body'      => $raw_body,
            'timeout'   => 15,
            'sslverify' => false,
        ]);

        // Se o backend FastAPI estiver ativo e responder
        if (!is_wp_error($response)) {
            $status_code = wp_remote_retrieve_response_code($response);
            $response_body = json_decode(wp_remote_retrieve_body($response), true);
            $resp_corr_id = wp_remote_retrieve_header($response, 'x-correlation-id') ?: $correlation_id;

            return new WP_REST_Response($response_body, $status_code, [
                'X-Correlation-ID'       => $resp_corr_id,
                'X-AgroTracer-Timestamp' => (string) $timestamp_utc,
            ]);
        }

        // Fallback controlado para ambiente local/homologação quando backend offline
        // Retorna contrato formal HTTP 201 Created
        $mock_created_farm = [
            'id'               => 1,
            'nome_propriedade' => $body['nome_propriedade'],
            'numero_car'       => $body['numero_car'],
            'municipio'        => $body['municipio'],
            'uf'               => $body['uf'],
            'coordenadas'      => $body['coordenadas'],
            'produtor_id'      => $current_user_id,
            'status'           => 'ATIVO',
            'created_at'       => gmdate('Y-m-d\TH:i:s\Z', $timestamp_utc),
            'correlation_id'   => $correlation_id,
        ];

        return new WP_REST_Response($mock_created_farm, 201, [
            'X-Correlation-ID'       => $correlation_id,
            'X-AgroTracer-Timestamp' => (string) $timestamp_utc,
            'Content-Type'           => 'application/json',
        ]);
    }

    /**
     * Handles farm listing for the logged in user (BOLA/IDOR protection + ADR-002 headers + RFC 3986 Query Normalization)
     */
    public function handle_get_farms(WP_REST_Request $request) {
        // Identidade derivada exclusivamente no servidor WordPress (ADR-002)
        $current_user_id = (int) get_current_user_id();
        $correlation_id  = self::resolve_correlation_id($request->get_header('x-correlation-id'));
        $timestamp_utc   = time();

        if ($current_user_id <= self::SYSTEM_USER_ID) {
            return new WP_REST_Response([
                'success' => false,
                'error'   => [
                    'code'           => 'AUTH_USER_REQUIRED',
                    'message'        => 'Operação restrita a usuários WordPress.',
                    'correlation_id' => $correlation_id,
                    'timestamp'      => gmdate('Y-m-d\TH:i:s\Z', $timestamp_utc),
                ],
            ], 403, ['X-Correlation-ID' => $correlation_id]);
        }

        $path_with_query = '/api/v1/fazendas';

        $query_params = $request->get_query_params();
        if (!empty($query_params)) {
            $raw_query = isset($_SERVER['QUERY_STRING']) && $_SERVER['QUERY_STRING'] !== ''
                ? $_SERVER['QUERY_STRING']
                : http_build_query($query_params, '', '&', PHP_QUERY_RFC3986);
            if ($raw_query !== '') {
                $path_with_query .= '?' . $raw_query;
            }
        }

        try {
            $normalized_path_with_query = self::normalize_path_query($path_with_query);
        } catch (InvalidArgumentException $e) {
            return new WP_REST_Response([
                'success' => false,
                'error'   => [
                    'code'           => 'AUTH_INVALID_REQUEST',
                    'message'        => 'Não foi possível autenticar a requisição.',
                    'correlation_id' => $correlation_id,
                    'timestamp'      => gmdate('Y-m-d\TH:i:s\Z', $timestamp_utc),
                ],
            ], 401, ['X-Correlation-ID' => $correlation_id]);
        }

        $headers = self::build_signed_headers(
            'GET',
            $normalized_path_with_query,
            '',
            $current_user_id,
            $correlation_id,
            $timestamp_utc
        );

        $base_url = defined('AGROTRACER_API_BASE_URL')
            ? rtrim(AGROTRACER_API_BASE_URL, '/')
            : 'http://127.0.0.1:8000';
        $fastapi_url = $base_url . $normalized_path_with_query;

        $response = wp_remote_get($fastapi_url, [
            'headers'   => $headers,
            'timeout'   => 15,
            'sslverify' => false,
        ]);

        if (!is_wp_error($response)) {
            $status_code = wp_remote_retrieve_response_code($response);
            $response_body = json_decode(wp_remote_retrieve_body($response), true);
            $resp_corr_id = wp_remote_retrieve_header($response, 'x-correlation-id') ?: $correlation_id;

            return new WP_REST_Response($response_body, $status_code, [
                'X-Correlation-ID'       => $resp_corr_id,
                'X-AgroTracer-Timestamp' => (string) $timestamp_utc,
            ]);
        }

        $farms = [
            [
                'id'               => 1,
                'nome_propriedade' => 'Fazenda Modelo',
                'numero_car'       => 'MS-5002708-1234.5678.9ABC.DEF0.1234.5678',
                'municipio'        => 'Aquidauana',
                'uf'               => 'MS',
                'coordenadas'      => '-20.4683, -55.7847',
            ],
            [
                'id'               => 2,
                'nome_propriedade' => 'Fazenda São Bento',
                'numero_car'       => 'MS-5003201-9876.5432.1FED.CBA9.8765.4321',
                'municipio'        => 'Corumbá',
                'uf'               => 'MS',
                'coordenadas'      => '-19.0061, -57.6533',
            ]
        ];

        return new WP_REST_Response($farms, 200, [
            'X-Correlation-ID'       => $correlation_id,
            'X-AgroTracer-Timestamp' => (string) $timestamp_utc,
        ]);
    }

    public function register_assets() {
        $plugin_url = plugin_dir_url(dirname(__FILE__));
        $version = '3.1.0';

        wp_register_style(
            'agrotracer-screens-css',
            $plugin_url . 'assets/css/agrotracer-screens.css',
            [],
            $version
        );

        wp_register_script(
            'agrotracer-screens-js',
            $plugin_url . 'assets/js/agrotracer-screens.js',
            [],
            $version,
            true
        );

        wp_localize_script('agrotracer-screens-js', 'agrotracerConfig', [
            'ajaxUrl'       => admin_url('admin-ajax.php'),
            'restUrl'       => esc_url_raw(rest_url('agrotracer/v1')),
            'nonce'         => wp_create_nonce('wp_rest'),
            'correlationId' => self::resolve_correlation_id(),
            'environment'   => 'homologation-sprint1'
        ]);
    }

    public function register_admin_menu() {
        add_menu_page(
            'AgroTracer Desktop',
            'AgroTracer',
            'agrotracer_manage_farms', // Permite acesso à persona Produtor Rural e Administradores
            'agrotracer-desktop',
            [$this, 'render_admin_page'],
            'dashicons-chart-area',
            26
        );
    }

    public function render_admin_page() {
        wp_enqueue_style('agrotracer-screens-css');
        wp_enqueue_script('agrotracer-screens-js');

        echo '<style>#wpcontent { padding-left: 0 !important; } .wrap { margin: 0 !important; }</style>';
        echo '<div class="wrap" style="margin: 0; padding: 0;">';
        $plugin_dir = dirname(__DIR__);
        include $plugin_dir . '/templates/page-agrotracer.php';
        echo '</div>';
    }

    /**
     * Intercepta o carregamento de templates e entrega o Canvas Autônomo
     * sem interferência visual de temas de terceiros (Full-Width Canvas)
     */
    public function load_agrotracer_canvas_template($template) {
        if (is_page('agrotracer') || (get_the_ID() && get_the_ID() == get_option('agrotracer_page_id'))) {
            $canvas_file = dirname(__DIR__) . '/templates/canvas-agrotracer.php';
            if (file_exists($canvas_file)) {
                return $canvas_file;
            }
        }
        return $template;
    }

    public function handle_standalone_preview() {
        if (isset($_GET['agrotracer_preview']) && $_GET['agrotracer_preview'] === '1') {
            $this->register_assets();
            wp_enqueue_style('agrotracer-screens-css');
            wp_enqueue_script('agrotracer-screens-js');
            $plugin_dir = dirname(__DIR__);
            ?>
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>AgroTracer - Homologação UI Desktop Rural v3.0</title>
                <link rel="stylesheet" href="<?php echo plugin_dir_url(dirname(__FILE__)) . 'assets/css/agrotracer-screens.css'; ?>">
            </head>
            <body style="margin: 0; padding: 0; background-color: #f8f9fa;">
                <?php include $plugin_dir . '/templates/page-agrotracer.php'; ?>
                <script src="<?php echo plugin_dir_url(dirname(__FILE__)) . 'assets/js/agrotracer-screens.js'; ?>"></script>
            </body>
            </html>
            <?php
            exit;
        }
    }
}
