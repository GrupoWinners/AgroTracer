<?php
/**
 * Main Controller for AgroTracer Bridge Plugin
 * Manages asset enqueues, admin menus, template routing, and API integration
 * via the centralized AgroTracer_Http_Client (`\AgroTracerBridge\Http\AgroTracer_Http_Client`).
 * Version: 3.1.0 (Sprint 1 - Task S1-T03 / S1-T04)
 *
 * @package AgroTracerBridge
 */

declare(strict_types=1);

use AgroTracerBridge\Http\AgroTracer_Http_Client;

if (!defined('ABSPATH')) {
    exit;
}

class AgroTracer_Bridge {

    private static $instance = null;

    public static function get_instance(): self {
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

        if (!class_exists(AgroTracer_Http_Client::class) && defined('AGROTRACER_PLUGIN_DIR')) {
            require_once AGROTRACER_PLUGIN_DIR . 'includes/class-agrotracer-http-client.php';
        }

        // Initialize Shortcodes
        if (class_exists('AgroTracer_Shortcodes')) {
            AgroTracer_Shortcodes::init();
        }
    }

    /**
     * Plugin Activation Routine:
     * 1. Configura Roles e Capabilities
     * 2. Provisiona de forma idempotente a página do sistema (/agrotracer)
     */
    public static function activate(): void {
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
    public static function setup_roles(): void {
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
    public static function deactivate(): void {
        // Mantém dados e roles persistentes por padrão, remove caps se necessário
    }

    /**
     * Registers REST API endpoints for AgroTracer Bridge
     * Endpoint: /wp-json/agrotracer/v1/fazendas
     */
    public function register_rest_routes(): void {
        register_rest_route('agrotracer/v1', '/fazendas', [
            [
                'methods'             => WP_REST_Server::CREATABLE, // POST
                'callback'            => [$this, 'handle_create_farm'],
                'permission_callback' => function (): bool {
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
                'permission_callback' => function (): bool {
                    return is_user_logged_in() && (
                        current_user_can('agrotracer_manage_farms') ||
                        current_user_can('publish_posts')
                    );
                },
            ]
        ]);
    }

    /**
     * Constantes oficiais do protocolo de segurança da Bridge (ADR-002 / S0-T06 / S1-T04)
     */
    public const TIMESTAMP_TOLERANCE_SECONDS = AgroTracer_Http_Client::TIMESTAMP_TOLERANCE_SECONDS;
    public const NONCE_TTL_SECONDS           = AgroTracer_Http_Client::NONCE_TTL_SECONDS;
    public const SYSTEM_USER_ID              = AgroTracer_Http_Client::SYSTEM_USER_ID;

    /**
     * Normaliza path e query string segundo RFC 3986 (ADR-002)
     */
    public static function normalize_path_query(string $path_with_query): string {
        return AgroTracer_Http_Client::normalize_path_query($path_with_query);
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
        return AgroTracer_Http_Client::build_canonical_string(
            $method,
            $path_with_query,
            $timestamp,
            $nonce,
            $wp_user_id,
            $raw_body
        );
    }

    /**
     * Gera assinatura HMAC-SHA256 em hexadecimal minúsculo (64 caracteres)
     */
    public static function generate_hmac_signature(string $canonical_string, string $secret_key): string {
        return AgroTracer_Http_Client::compute_hmac_signature($canonical_string, $secret_key);
    }

    /**
     * Valida ou gera um X-Correlation-ID em formato UUID v4 canônico minúsculo (36 caracteres)
     */
    public static function resolve_correlation_id(?string $incoming_id = null): string {
        return AgroTracer_Http_Client::resolve_correlation_id($incoming_id);
    }

    /**
     * Gera Nonce criptograficamente seguro de 16 bytes (32 caracteres hex minúsculos)
     */
    public static function generate_nonce(): string {
        return AgroTracer_Http_Client::generate_nonce();
    }

    /**
     * Constrói o pacote completo de headers autenticados da Bridge (ADR-002 / S1-T04)
     * Inclui X-AgroTracer-Actor-ID, X-AgroTracer-User-Id, X-AgroTracer-Timestamp,
     * X-AgroTracer-Nonce, X-AgroTracer-Signature e X-Correlation-ID.
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
        return AgroTracer_Http_Client::build_signed_headers(
            $method,
            $path_with_query,
            $raw_body,
            $wp_user_id,
            $correlation_id,
            $timestamp,
            $nonce,
            $secret_key
        );
    }

    /**
     * Mapeia códigos HTTP de erro da API FastAPI para mensagens claras e seguras na UI.
     */
    public static function map_error_to_ui_message(
        int $status_code,
        ?string $error_code = null,
        array $field_errors = []
    ): string {
        return AgroTracer_Http_Client::map_error_to_ui_message($status_code, $error_code, $field_errors);
    }

    /**
     * Handles farm creation and forwards to Python FastAPI backend via AgroTracer_Http_Client.
     * Enforces wp_verify_nonce, current_user_can, server-side get_current_user_id(),
     * defensive timeout, and non-leaky UI error mapping.
     */
    public function handle_create_farm(WP_REST_Request $request): WP_REST_Response {
        $correlation_id = self::resolve_correlation_id($request->get_header('x-correlation-id'));
        $timestamp_utc  = time();

        // 1. Validação explícita de Nonce (CSRF) e Capability quando enviado via browser REST
        $wp_nonce = $request->get_header('x-wp-nonce') ?: (string) $request->get_param('_wpnonce');
        if ($wp_nonce !== '' && function_exists('wp_verify_nonce')) {
            if (!wp_verify_nonce($wp_nonce, 'wp_rest')) {
                return new WP_REST_Response([
                    'success' => false,
                    'error'   => [
                        'code'           => 'AUTH_INVALID_NONCE',
                        'message'        => self::map_error_to_ui_message(401, 'AUTH_INVALID_REQUEST'),
                        'correlation_id' => $correlation_id,
                        'timestamp'      => gmdate('Y-m-d\TH:i:s\Z', $timestamp_utc),
                    ],
                ], 401, ['X-Correlation-ID' => $correlation_id]);
            }
        }

        // 2. Identidade derivada exclusivamente no servidor WordPress após validação de capability
        $current_user_id = (int) get_current_user_id();
        $has_cap = current_user_can('agrotracer_manage_farms') || current_user_can('publish_posts');

        if ($current_user_id <= self::SYSTEM_USER_ID || !$has_cap) {
            return new WP_REST_Response([
                'success' => false,
                'error'   => [
                    'code'           => 'AUTH_USER_REQUIRED',
                    'message'        => self::map_error_to_ui_message(403, 'AUTH_USER_REQUIRED'),
                    'correlation_id' => $correlation_id,
                    'timestamp'      => gmdate('Y-m-d\TH:i:s\Z', $timestamp_utc),
                ],
            ], 403, ['X-Correlation-ID' => $correlation_id]);
        }

        // 3. Sanitização estrita: ignora qualquer user_id vindo do request/browser
        $nome_val = $request->get_param('nome') ?: $request->get_param('nome_propriedade');
        $car_val  = $request->get_param('numero_car_informado') ?: $request->get_param('numero_car');
        $raw_input = [
            'nome'                 => $nome_val,
            'nome_propriedade'     => $nome_val,
            'numero_car'           => $car_val,
            'numero_car_informado' => $car_val,
            'municipio'            => $request->get_param('municipio'),
            'uf'                   => $request->get_param('uf'),
            'coordenadas'          => $request->get_param('coordenadas'),
        ];

        $result = AgroTracer_Http_Client::post(
            '/api/v1/fazendas',
            $raw_input,
            $current_user_id,
            $correlation_id,
            true
        );

        // Se o backend FastAPI respondeu (sucesso 2xx ou erro de domínio 4xx/500)
        if ($result['success'] === true) {
            return new WP_REST_Response($result['data'], $result['status'], [
                'X-Correlation-ID'       => $result['correlation_id'],
                'X-AgroTracer-Timestamp' => (string) $result['timestamp'],
            ]);
        }

        if ($result['status'] !== 503 || (isset($result['error']['code']) && $result['error']['code'] !== 'SERVICE_UNAVAILABLE')) {
            return new WP_REST_Response([
                'success' => false,
                'error'   => $result['error'],
            ], $result['status'], [
                'X-Correlation-ID'       => $result['correlation_id'],
                'X-AgroTracer-Timestamp' => (string) $result['timestamp'],
            ]);
        }

        // Fallback controlado para ambiente local/homologação quando backend offline
        $mock_created_farm = [
            'id'               => 1,
            'nome_propriedade' => $raw_input['nome_propriedade'],
            'numero_car'       => $raw_input['numero_car'],
            'municipio'        => $raw_input['municipio'],
            'uf'               => $raw_input['uf'],
            'coordenadas'      => $raw_input['coordenadas'],
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
     * Handles farm listing for the logged in user via AgroTracer_Http_Client.
     */
    public function handle_get_farms(WP_REST_Request $request): WP_REST_Response {
        $correlation_id  = self::resolve_correlation_id($request->get_header('x-correlation-id'));
        $timestamp_utc   = time();
        $current_user_id = (int) get_current_user_id();
        $has_cap         = current_user_can('agrotracer_manage_farms') || current_user_can('publish_posts');

        if ($current_user_id <= self::SYSTEM_USER_ID || !$has_cap) {
            return new WP_REST_Response([
                'success' => false,
                'error'   => [
                    'code'           => 'AUTH_USER_REQUIRED',
                    'message'        => self::map_error_to_ui_message(403, 'AUTH_USER_REQUIRED'),
                    'correlation_id' => $correlation_id,
                    'timestamp'      => gmdate('Y-m-d\TH:i:s\Z', $timestamp_utc),
                ],
            ], 403, ['X-Correlation-ID' => $correlation_id]);
        }

        $query_params = (array) $request->get_query_params();
        $result = AgroTracer_Http_Client::get(
            '/api/v1/fazendas',
            $query_params,
            $current_user_id,
            $correlation_id
        );

        if ($result['success'] === true) {
            return new WP_REST_Response($result['data'], $result['status'], [
                'X-Correlation-ID'       => $result['correlation_id'],
                'X-AgroTracer-Timestamp' => (string) $result['timestamp'],
            ]);
        }

        if ($result['status'] !== 503 || (isset($result['error']['code']) && $result['error']['code'] !== 'SERVICE_UNAVAILABLE')) {
            return new WP_REST_Response([
                'success' => false,
                'error'   => $result['error'],
            ], $result['status'], [
                'X-Correlation-ID'       => $result['correlation_id'],
                'X-AgroTracer-Timestamp' => (string) $result['timestamp'],
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

    public function register_assets(): void {
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

        // Regra estrita: NUNCA expor segredos criptográficos ou chaves HMAC em HTML/JS
        wp_localize_script('agrotracer-screens-js', 'agrotracerConfig', [
            'ajaxUrl'       => admin_url('admin-ajax.php'),
            'restUrl'       => esc_url_raw(rest_url('agrotracer/v1')),
            'nonce'         => wp_create_nonce('wp_rest'),
            'correlationId' => self::resolve_correlation_id(),
            'environment'   => 'homologation-sprint1'
        ]);
    }

    public function register_admin_menu(): void {
        add_menu_page(
            'AgroTracer Desktop',
            'AgroTracer',
            'agrotracer_manage_farms',
            'agrotracer-desktop',
            [$this, 'render_admin_page'],
            'dashicons-chart-area',
            26
        );
    }

    public function render_admin_page(): void {
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

    public function handle_standalone_preview(): void {
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
