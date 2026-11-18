<?php
/**
 * Automated Test Suite for Sprint 5 - Task S5-T05
 * Epic: [EP-S5] Sprint 5 — Certificado PDF, QR e consulta pública
 * Escopo: Página pública de verificação, DTO minimizado (RN-13),
 *         badges semânticos (Válido/Revogado) e geração local de QR Code.
 *
 * @package AgroTracerBridge\Tests
 */

declare(strict_types=1);

namespace {
    if (!function_exists('add_action')) {
        function add_action($hook, $callback, $priority = 10, $accepted_args = 1) {}
    }
    if (!function_exists('add_filter')) {
        function add_filter($hook, $callback, $priority = 10, $accepted_args = 1) {}
    }
    if (!function_exists('add_shortcode')) {
        function add_shortcode($tag, $callback) {}
    }
    if (!function_exists('register_rest_route')) {
        function register_rest_route($namespace, $route, $args = []) {}
    }
    if (!function_exists('esc_html')) {
        function esc_html($text) {
            return htmlspecialchars((string) $text, ENT_QUOTES, 'UTF-8');
        }
    }
    if (!function_exists('esc_attr')) {
        function esc_attr($text) {
            return htmlspecialchars((string) $text, ENT_QUOTES, 'UTF-8');
        }
    }
    if (!function_exists('esc_url')) {
        function esc_url($url) {
            return htmlspecialchars((string) $url, ENT_QUOTES, 'UTF-8');
        }
    }

    if (!class_exists('WP_REST_Request')) {
        class WP_REST_Request {
            private string $method;
            private string $route;
            private array $params = [];
            private array $headers = [];
            public function __construct(string $method = 'GET', string $route = '') {
                $this->method = $method;
                $this->route = $route;
            }
            public function set_param(string $key, $value): void { $this->params[$key] = $value; }
            public function get_param(string $key) { return $this->params[$key] ?? null; }
            public function get_header(string $key) { return $this->headers[strtolower($key)] ?? null; }
            public function set_header(string $key, string $val): void { $this->headers[strtolower($key)] = $val; }
            public function get_query_params(): array { return $this->params; }
        }
    }

    if (!class_exists('WP_REST_Response')) {
        class WP_REST_Response {
            private $data;
            private int $status;
            private array $headers;
            public function __construct($data = null, int $status = 200, array $headers = []) {
                $this->data = $data;
                $this->status = $status;
                $this->headers = $headers;
            }
            public function get_status(): int { return $this->status; }
            public function get_data() { return $this->data; }
            public function get_headers(): array { return $this->headers; }
        }
    }
}

namespace AgroTracerBridge\Tests {

    require_once __DIR__ . '/bootstrap.php';
    require_once dirname(__DIR__) . '/includes/class-agrotracer-http-client.php';
    require_once dirname(__DIR__) . '/includes/class-agrotracer-shortcodes.php';
    require_once dirname(__DIR__) . '/includes/class-agrotracer-bridge.php';

    use AgroTracer_Bridge;
    use AgroTracer_Shortcodes;
    use AgroTracer_WP_Test_Mock_State;
    use AgroTracerBridge\Http\AgroTracer_Http_Client;
    use PHPUnit\Framework\TestCase;

    class AgroTracerS5T05ConsultaPublicaTest extends TestCase {

        private string $templatesDir;
        private string $assetsDir;

        public function setUp(): void {
            parent::setUp();
            AgroTracer_WP_Test_Mock_State::reset();
            $_GET = [];
            $this->templatesDir = dirname(__DIR__) . '/templates';
            $this->assetsDir = dirname(__DIR__) . '/assets';
        }

        public function test_get_public_does_not_require_actor_or_send_hmac_headers(): void {
            AgroTracer_WP_Test_Mock_State::$current_user_id = 0;

            AgroTracer_WP_Test_Mock_State::$remote_handler = function (string $url, array $args) {
                return [
                    'response' => ['code' => 200, 'message' => 'OK'],
                    'headers'  => ['x-correlation-id' => $args['headers']['X-Correlation-ID']],
                    'body'     => json_encode([
                        'certificado_id' => 17,
                        'lote_id'        => 2,
                        'status'         => 'VALIDO',
                    ]),
                ];
            };

            $res = AgroTracer_Http_Client::get_public('/api/v1/certificados/publico', ['token' => 'tok_abc']);
            $this->assertTrue($res['success']);
            $this->assertEquals(200, $res['status']);

            $sent = AgroTracer_WP_Test_Mock_State::$dispatched_requests[0];
            $this->assertStringContainsString('/api/v1/certificados/publico?token=tok_abc', $sent['url']);
            $this->assertArrayNotHasKey('X-AgroTracer-Actor-ID', $sent['args']['headers']);
            $this->assertArrayNotHasKey('X-AgroTracer-User-Id', $sent['args']['headers']);
            $this->assertArrayNotHasKey('X-AgroTracer-Signature', $sent['args']['headers']);
        }

        public function test_public_rest_endpoint_minimizes_dto_and_sets_security_headers(): void {
            AgroTracer_WP_Test_Mock_State::$current_user_id = 0;
            $bridge = AgroTracer_Bridge::get_instance();
            $this->assertTrue(method_exists($bridge, 'handle_get_certificado_publico'));

            AgroTracer_WP_Test_Mock_State::$remote_handler = function (string $url, array $args) {
                return [
                    'response' => ['code' => 200, 'message' => 'OK'],
                    'headers'  => ['x-correlation-id' => $args['headers']['X-Correlation-ID']],
                    'body'     => json_encode([
                        'certificado_id'       => 17,
                        'lote_id'              => 5,
                        'status'               => 'VALIDO',
                        'emitido_em'           => '2026-11-18T20:00:00Z',
                        'versao_metodo'        => 'CARBONENGINE-MVP-1.0',
                        'versao_parametros'    => 'S4-DEMO-1',
                        'source_types'         => ['SYNTHETIC'],
                        'synthetic'            => true,
                        'aviso_proveniencia'   => 'SYNTHETIC - DEMONSTRAÇÃO DIDÁTICA.',
                        'data_abate'           => '2026-06-01',
                        'numero_animais_abate' => 50,
                        'resultados'           => [
                            'emissao_total_kg_co2e'  => '13650.000000',
                            'intensidade_kg_co2e_kg' => '0.953878',
                            'unidade_emissao'        => 'kg CO2e',
                            'unidade_intensidade'    => 'kg CO2e/kg de carcaça',
                        ],
                        'snapshot_sha256'      => str_repeat('b', 64),
                        'pdf_sha256'           => null,
                        // Campos proibidos simulando tentativa de vazamento:
                        'produtor_nome'        => 'João da Silva',
                        'cpf'                  => '123.456.789-00',
                        'email'                => 'privado@fazenda.example',
                        'source_uri'           => 'https://interno.example/segredo',
                    ]),
                ];
            };

            $req = new \WP_REST_Request('GET', '/agrotracer/v1/certificados/publico');
            $req->set_param('token', 'tok_publico_valido_43_chars_abcdef123456789');

            $resp = $bridge->handle_get_certificado_publico($req);
            $this->assertEquals(200, $resp->get_status());

            $headers = $resp->get_headers();
            $this->assertSame('no-store', $headers['Cache-Control']);
            $this->assertSame('no-referrer', $headers['Referrer-Policy']);
            $this->assertSame('noindex, nofollow', $headers['X-Robots-Tag']);
            $this->assertSame('nosniff', $headers['X-Content-Type-Options']);

            $data = $resp->get_data();
            $this->assertSame('VALIDO', $data['status']);
            $this->assertSame('13650.000000', $data['resultados']['emissao_total_kg_co2e']);
            $this->assertArrayNotHasKey('produtor_nome', $data);
            $this->assertArrayNotHasKey('cpf', $data);
            $this->assertArrayNotHasKey('email', $data);
            $this->assertArrayNotHasKey('source_uri', $data);
        }

        public function test_public_page_renders_semantic_badges_synthetic_and_zero_pii(): void {
            AgroTracer_WP_Test_Mock_State::$current_user_id = 0;

            AgroTracer_WP_Test_Mock_State::$remote_handler = function (string $url, array $args) {
                return [
                    'response' => ['code' => 200, 'message' => 'OK'],
                    'headers'  => ['x-correlation-id' => $args['headers']['X-Correlation-ID']],
                    'body'     => json_encode([
                        'certificado_id'       => 22,
                        'lote_id'              => 9,
                        'status'               => 'VALIDO',
                        'emitido_em'           => '2026-11-18T21:00:00Z',
                        'versao_metodo'        => 'CARBONENGINE-MVP-1.0',
                        'versao_parametros'    => '<script>alert(1)</script>',
                        'source_types'         => ['SYNTHETIC'],
                        'synthetic'            => true,
                        'aviso_proveniencia'   => 'SYNTHETIC - DEMONSTRAÇÃO DIDÁTICA.',
                        'data_abate'           => '2026-06-01',
                        'numero_animais_abate' => 45,
                        'resultados'           => [
                            'emissao_total_kg_co2e'  => '12285.1234',
                            'intensidade_kg_co2e_kg' => '0.9421',
                            'unidade_emissao'        => 'kg CO2e',
                            'unidade_intensidade'    => 'kg CO2e/kg de carcaça',
                        ],
                        'snapshot_sha256'      => str_repeat('c', 64),
                        'pdf_sha256'           => str_repeat('d', 64),
                        'cpf'                  => '999.888.777-66',
                        'telefone'             => '(31) 99999-0000',
                    ]),
                ];
            };

            $_GET['token'] = 'TOKEN_SECRETO_43_CHARS_0123456789abcdefghij';
            $html = AgroTracer_Shortcodes::render_public_certificate();

            $this->assertStringContainsString('id="public-cert-status-badge"', $html);
            $this->assertStringContainsString('class="agro-badge success"', $html);
            $this->assertStringContainsString('Válido', $html);
            $this->assertStringContainsString('id="public-cert-synthetic-banner"', $html);
            $this->assertStringContainsString('12285.1234', $html);
            $this->assertStringContainsString('0.9421', $html);
            $this->assertStringContainsString(str_repeat('c', 64), $html);
            $this->assertStringContainsString(str_repeat('d', 64), $html);
            $this->assertStringContainsString('&lt;script&gt;alert(1)&lt;/script&gt;', $html);
            $this->assertStringNotContainsString('<script>alert(1)</script>', $html);
            $this->assertStringNotContainsString('999.888.777-66', $html);
            $this->assertStringNotContainsString('(31) 99999-0000', $html);
            $this->assertStringNotContainsString('TOKEN_SECRETO_43_CHARS', $html);
        }

        public function test_public_page_renders_danger_badge_for_revoked_and_generic_errors(): void {
            AgroTracer_WP_Test_Mock_State::$current_user_id = 0;

            // 1. Certificado REVOGADO -> badge danger
            AgroTracer_WP_Test_Mock_State::$remote_handler = function (string $url, array $args) {
                return [
                    'response' => ['code' => 200, 'message' => 'OK'],
                    'headers'  => ['x-correlation-id' => $args['headers']['X-Correlation-ID']],
                    'body'     => json_encode([
                        'certificado_id'       => 23,
                        'lote_id'              => 10,
                        'status'               => 'REVOGADO',
                        'emitido_em'           => '2026-11-18T21:00:00Z',
                        'versao_metodo'        => 'CARBONENGINE-MVP-1.0',
                        'versao_parametros'    => 'S4-DEMO-1',
                        'source_types'         => ['SYNTHETIC'],
                        'synthetic'            => true,
                        'data_abate'           => '2026-06-01',
                        'numero_animais_abate' => 10,
                        'resultados'           => [
                            'emissao_total_kg_co2e'  => '500.00',
                            'intensidade_kg_co2e_kg' => '0.800',
                        ],
                        'snapshot_sha256'      => str_repeat('e', 64),
                    ]),
                ];
            };

            $_GET['token'] = 'TOKEN_REVOGADO_01';
            $revHtml = AgroTracer_Shortcodes::render_public_certificate();
            $this->assertStringContainsString('class="agro-badge danger"', $revHtml);
            $this->assertStringContainsString('Revogado / Invalidado', $revHtml);
            $this->assertStringContainsString('id="public-cert-revoked-alert"', $revHtml);

            // 2. 404 genérico (RN-13)
            AgroTracer_WP_Test_Mock_State::$remote_handler = function (string $url, array $args) {
                return [
                    'response' => ['code' => 404, 'message' => 'Not Found'],
                    'headers'  => ['x-correlation-id' => $args['headers']['X-Correlation-ID']],
                    'body'     => json_encode([
                        'error' => ['code' => 'CERTIFICADO_NAO_ENCONTRADO', 'message' => 'Certificado nao encontrado.'],
                    ]),
                ];
            };
            $_GET['token'] = 'nao_existe';
            $err404 = AgroTracer_Shortcodes::render_public_certificate();
            $this->assertStringContainsString('Certificado não encontrado.', $err404);
            $this->assertStringNotContainsString('nao_existe', $err404);

            // 3. 429 rate limit
            AgroTracer_WP_Test_Mock_State::$remote_handler = function (string $url, array $args) {
                return [
                    'response' => ['code' => 429, 'message' => 'Too Many Requests'],
                    'headers'  => ['x-correlation-id' => $args['headers']['X-Correlation-ID']],
                    'body'     => json_encode([
                        'error' => ['code' => 'LIMITE_CONSULTAS', 'message' => 'Tente novamente em um minuto.'],
                    ]),
                ];
            };
            $err429 = AgroTracer_Shortcodes::render_public_certificate();
            $this->assertStringContainsString('Limite de consultas atingido.', $err429);
        }

        public function test_local_qr_code_ui_without_external_qr_apis(): void {
            $fechamentoHtml = file_get_contents($this->templatesDir . '/fechamento.php');
            $jsContent      = file_get_contents($this->assetsDir . '/js/agrotracer-screens.js');

            $this->assertStringContainsString('id="cert-res-qr-container"', $fechamentoHtml);
            $this->assertStringContainsString('id="cert-res-public-open-link"', $fechamentoHtml);
            $this->assertStringContainsString('function buildQrCodeSvg(text)', $jsContent);
            $this->assertStringContainsString('certResQrContainer.innerHTML = buildQrCodeSvg(publicUrl)', $jsContent);

            // Nunca vaza token para serviços externos de geração de QR
            $this->assertStringNotContainsString('api.qrserver.com', $jsContent);
            $this->assertStringNotContainsString('chart.googleapis.com', $jsContent);
            $this->assertStringNotContainsString('quickchart.io', $jsContent);
        }
    }

    if (php_sapi_name() === 'cli' && basename(__FILE__) === basename($_SERVER['SCRIPT_FILENAME'] ?? '')) {
        echo "=========================================================================\n";
        echo "AgroTracer Sprint 5 Test Suite: Task S5-T05 (Consulta Publica & QR Local)\n";
        echo "Ambiente: PHP " . PHP_VERSION . " | WordPress Test Harness\n";
        echo "=========================================================================\n";

        $suite = new AgroTracerS5T05ConsultaPublicaTest();
        $methods = get_class_methods($suite);
        $testMethods = array_filter($methods, fn($m) => str_starts_with($m, 'test_'));

        $passed = 0;
        $failed = 0;
        $start = microtime(true);

        foreach ($testMethods as $method) {
            try {
                $suite->setUp();
                $suite->$method();
                echo " [PASS] {$method}\n";
                $passed++;
            } catch (\Throwable $e) {
                echo " [FAIL] {$method}: " . $e->getMessage() . "\n";
                $failed++;
            }
        }

        $elapsed = round((microtime(true) - $start) * 1000, 2);
        echo "-------------------------------------------------------------------------\n";
        echo "Resultado: {$passed} passaram | {$failed} falharam | Tempo: {$elapsed} ms\n";
        echo "=========================================================================\n";

        exit($failed === 0 ? 0 : 1);
    }
}
