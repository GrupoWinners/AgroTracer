<?php
/**
 * Automated Test Suite for Sprint 3 - Task S3-T04
 * Epic: [EP-S3] Sprint 3 — Manejo nutricional e método de parâmetros
 * Escopo: Tela de timeline de manejo com cadastro de períodos e mensagem de conflito que identifica o período conflitante.
 * Critérios de aceite:
 * 1. Usuário identifica o período conflitante
 * 2. Unidades e datas claras
 * 3. Estados de UX completos (carregamento, vazio, conflito, formulário)
 *
 * @package AgroTracerBridge\Tests
 */

declare(strict_types=1);

namespace {
    // Stubs no namespace global do WordPress para execução CLI Standalone
    if (!function_exists('add_action')) {
        function add_action($hook, $callback, $priority = 10, $accepted_args = 1) {}
    }
    if (!function_exists('add_filter')) {
        function add_filter($hook, $callback, $priority = 10, $accepted_args = 1) {}
    }
    if (!function_exists('register_rest_route')) {
        function register_rest_route($namespace, $route, $args = []) {}
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
        }
    }
}

namespace AgroTracerBridge\Tests {

    require_once __DIR__ . '/bootstrap.php';
    require_once dirname(__DIR__) . '/includes/class-agrotracer-http-client.php';
    require_once dirname(__DIR__) . '/includes/class-agrotracer-bridge.php';

    use AgroTracer_Bridge;
    use AgroTracer_WP_Test_Mock_State;
    use PHPUnit\Framework\TestCase;

    class AgroTracerS3T04TimelineManejoTest extends TestCase {

        private string $templatesDir;
        private string $assetsDir;

        public function setUp(): void {
            parent::setUp();
            AgroTracer_WP_Test_Mock_State::reset();
            $this->templatesDir = dirname(__DIR__) . '/templates';
            $this->assetsDir = dirname(__DIR__) . '/assets';
        }

        /**
         * Teste 1: Verifica existência e integridade dos templates da S3-T04
         */
        public function test_templates_exist_and_contain_required_identifiers(): void {
            $manejoFile = $this->templatesDir . '/manejo.php';
            $modalsFile = $this->templatesDir . '/modals.php';
            $pageFile   = $this->templatesDir . '/page-agrotracer.php';

            $this->assertTrue(file_exists($manejoFile), 'Template manejo.php deve existir');
            $this->assertTrue(file_exists($modalsFile), 'Template modals.php deve existir');
            $this->assertTrue(file_exists($pageFile),   'Template page-agrotracer.php deve existir');

            $manejoHtml = file_get_contents($manejoFile);
            $modalsHtml = file_get_contents($modalsFile);
            $pageHtml   = file_get_contents($pageFile);

            // Inclusão no layout principal
            $this->assertStringContainsString('include $plugin_dir . \'/templates/manejo.php\';', $pageHtml);

            // Container e ações da tela
            $this->assertStringContainsString('id="screen-manejo"', $manejoHtml);
            $this->assertStringContainsString('id="btn-open-create-manejo-modal"', $manejoHtml);
            $this->assertStringContainsString('id="select-manejo-lote"', $manejoHtml);
            $this->assertStringContainsString('id="manejo-timeline-container"', $manejoHtml);

            // Modal de cadastro
            $this->assertStringContainsString('id="modal-create-manejo"', $modalsHtml);
            $this->assertStringContainsString('id="form-create-manejo"', $modalsHtml);
            $this->assertStringContainsString('id="modal-manejo-data-inicio"', $modalsHtml);
            $this->assertStringContainsString('id="modal-manejo-data-fim"', $modalsHtml);
            $this->assertStringContainsString('id="btn-submit-create-manejo"', $modalsHtml);
        }

        /**
         * Teste 2: Critério de Aceite — Mensagem e identificação do período conflitante
         */
        public function test_conflict_identification_components_and_error_message(): void {
            $manejoHtml = file_get_contents($this->templatesDir . '/manejo.php');
            $modalsHtml = file_get_contents($this->templatesDir . '/modals.php');

            // Banner de conflito na tela principal identifica período conflitante
            $this->assertStringContainsString('id="manejo-conflict-banner"', $manejoHtml);
            $this->assertStringContainsString('id="conflict-period-range"', $manejoHtml);
            $this->assertStringContainsString('MANEJO_SOBREPOSTO (HTTP 409)', $manejoHtml);

            // Caixa de conflito inline dentro do modal
            $this->assertStringContainsString('id="modal-manejo-conflict-box"', $modalsHtml);
            $this->assertStringContainsString('id="modal-manejo-conflict-detail"', $modalsHtml);
            $this->assertStringContainsString('MANEJO_SOBREPOSTO', $modalsHtml);
        }

        /**
         * Teste 3: Critério de Aceite — Unidades e datas claras
         */
        public function test_units_and_dates_clarity_and_scientific_transparency(): void {
            $manejoHtml = file_get_contents($this->templatesDir . '/manejo.php');
            $modalsHtml = file_get_contents($this->templatesDir . '/modals.php');

            // Datas claras (indicação explícita inclusiva e formato)
            $this->assertStringContainsString('AAAA-MM-DD', $modalsHtml);
            $this->assertStringContainsString('dias inclusivos', $manejoHtml);

            // Unidades zootécnicas explícitas
            $this->assertStringContainsString('kg MS/cab/dia', $manejoHtml);
            $this->assertStringContainsString('% EB', $manejoHtml);
            $this->assertStringContainsString('kg CH4/cab/ano', $manejoHtml);
            $this->assertStringContainsString('kg MS/cab/dia', $modalsHtml);

            // Transparência científica sem alegação indevida (ADR S3-T02 / S3-T06)
            $this->assertStringContainsString('SYNTHETIC', $manejoHtml);
            $this->assertStringContainsString('Transparência Científica', $manejoHtml);
            $this->assertStringContainsString('v1.0-2026', $manejoHtml);
        }

        /**
         * Teste 4: Cuidado de Engenharia — Estados de UX completos
         */
        public function test_complete_ux_states_present(): void {
            $manejoHtml = file_get_contents($this->templatesDir . '/manejo.php');

            // Estado Vazio (Empty State)
            $this->assertStringContainsString('id="manejo-empty-state"', $manejoHtml);
            $this->assertStringContainsString('id="btn-empty-create-manejo"', $manejoHtml);

            // Estado de Carregamento (Loading State)
            $this->assertStringContainsString('id="manejo-loading-state"', $manejoHtml);
            $this->assertStringContainsString('agro-spinner', $manejoHtml);

            // Estado com Dados (Timeline Card)
            $this->assertStringContainsString('id="manejo-timeline-card"', $manejoHtml);
            $this->assertStringContainsString('id="kpi-manejo-dias"', $manejoHtml);
            $this->assertStringContainsString('id="kpi-timeline-integrity-badge"', $manejoHtml);
        }

        /**
         * Teste 5: Handlers REST da Bridge (FastAPI Proxy / Fallback) para Manejos e Parâmetros
         */
        public function test_bridge_controller_has_sprint3_handlers(): void {
            $bridge = AgroTracer_Bridge::get_instance();

            $this->assertTrue(method_exists($bridge, 'handle_create_manejo'), 'handle_create_manejo deve existir');
            $this->assertTrue(method_exists($bridge, 'handle_get_manejos'),   'handle_get_manejos deve existir');
            $this->assertTrue(method_exists($bridge, 'handle_get_parametros'),'handle_get_parametros deve existir');

            // Configura o remote_handler para responder como o backend FastAPI
            AgroTracer_WP_Test_Mock_State::$remote_handler = function(string $url, array $args) {
                $method = $args['method'] ?? 'GET';
                $body   = $args['body'] ?? '';
                $corrId = $args['headers']['X-Correlation-ID'] ?? 'test-corr-id';

                if ($method === 'GET' && strpos($url, '/manejos') !== false) {
                    return [
                        'response' => ['code' => 200, 'message' => 'OK'],
                        'headers'  => ['x-correlation-id' => $corrId],
                        'body'     => json_encode([
                            ['id' => 1, 'lote_id' => 1, 'inicio' => '2026-11-01', 'fim' => '2026-11-10', 'parametro_set_id' => 1, 'tipo_dieta' => 'PASTAGEM'],
                            ['id' => 2, 'lote_id' => 1, 'inicio' => '2026-11-11', 'fim' => '2026-11-30', 'parametro_set_id' => 1, 'tipo_dieta' => 'SUPLEMENTACAO_MINERAL'],
                        ]),
                    ];
                }

                if ($method === 'POST' && strpos($url, '/manejos') !== false) {
                    if (strpos($body, '2026-11-05') !== false) {
                        return [
                            'response' => ['code' => 409, 'message' => 'Conflict'],
                            'headers'  => ['x-correlation-id' => $corrId],
                            'body'     => json_encode([
                                'error' => [
                                    'code'           => 'MANEJO_SOBREPOSTO',
                                    'message'        => 'Existe sobreposição com o manejo já registrado de 2026-11-01 a 2026-11-10.',
                                    'detalhes'       => [
                                        'manejo_conflitante_id' => 1,
                                        'inicio'                => '2026-11-01',
                                        'fim'                   => '2026-11-10',
                                    ],
                                    'field_errors'   => [],
                                    'correlation_id' => $corrId,
                                ]
                            ]),
                        ];
                    }

                    return [
                        'response' => ['code' => 201, 'message' => 'Created'],
                        'headers'  => ['x-correlation-id' => $corrId],
                        'body'     => json_encode([
                            'id'               => 10,
                            'lote_id'          => 1,
                            'inicio'           => '2026-12-01',
                            'fim'              => '2026-12-15',
                            'parametro_set_id' => 1,
                            'tipo_dieta'       => 'PASTAGEM',
                        ]),
                    ];
                }

                return [
                    'response' => ['code' => 200, 'message' => 'OK'],
                    'headers'  => ['x-correlation-id' => $corrId],
                    'body'     => json_encode(['data' => []]),
                ];
            };

            // 1. Simula GET de manejos do lote 1
            $reqGet = new \WP_REST_Request('GET', '/agrotracer/v1/manejos');
            $reqGet->set_param('lote_id', 1);
            $resGet = $bridge->handle_get_manejos($reqGet);

            $this->assertSame(200, $resGet->get_status());
            $dataGet = $resGet->get_data();
            $this->assertTrue(is_array($dataGet));
            $this->assertTrue(count($dataGet) >= 1);
            $this->assertSame('2026-11-01', $dataGet[0]['inicio']);
            $this->assertSame('2026-11-10', $dataGet[0]['fim']);

            // 2. Simula criação de manejo com conflito de datas (sobreposição)
            $reqConflict = new \WP_REST_Request('POST', '/agrotracer/v1/manejos');
            $reqConflict->set_param('lote_id', 1);
            $reqConflict->set_param('inicio', '2026-11-05');
            $reqConflict->set_param('fim', '2026-11-15');
            $reqConflict->set_param('parametro_set_id', 1);
            $reqConflict->set_param('tipo_dieta', 'PASTAGEM');

            $resConflict = $bridge->handle_create_manejo($reqConflict);
            $this->assertSame(409, $resConflict->get_status());
            $dataConflict = $resConflict->get_data();
            $this->assertSame('MANEJO_SOBREPOSTO', $dataConflict['error']['code']);
            $this->assertStringContainsString('2026-11-01', $dataConflict['error']['message']);
            $this->assertStringContainsString('2026-11-10', $dataConflict['error']['message']);
            $this->assertTrue(isset($dataConflict['error']['detalhes']['inicio']));

            // 3. Simula criação de manejo sem sobreposição (sucesso contíguo)
            $reqSuccess = new \WP_REST_Request('POST', '/agrotracer/v1/manejos');
            $reqSuccess->set_param('lote_id', 1);
            $reqSuccess->set_param('inicio', '2026-12-01');
            $reqSuccess->set_param('fim', '2026-12-15');
            $reqSuccess->set_param('parametro_set_id', 1);
            $reqSuccess->set_param('tipo_dieta', 'PASTAGEM');

            $resSuccess = $bridge->handle_create_manejo($reqSuccess);
            $this->assertSame(201, $resSuccess->get_status());
            $dataSuccess = $resSuccess->get_data();
            $this->assertSame('2026-12-01', $dataSuccess['inicio']);
            $this->assertSame('2026-12-15', $dataSuccess['fim']);

            // 4. Consulta de parâmetros versionados
            $reqParam = new \WP_REST_Request('GET', '/agrotracer/v1/parametros');
            $resParam = $bridge->handle_get_parametros($reqParam);
            $this->assertSame(200, $resParam->get_status());
            $dataParam = $resParam->get_data();
            $this->assertSame('v1.0-2026', $dataParam[0]['versao']);
            $this->assertSame('SYNTHETIC', $dataParam[0]['source_type']);
        }
    }

    // Execução CLI Standalone
    if (php_sapi_name() === 'cli' && basename(__FILE__) === basename($_SERVER['SCRIPT_FILENAME'] ?? '')) {
        echo "=========================================================================\n";
        echo "AgroTracer Sprint 3 Test Suite: Task S3-T04 (Timeline de Manejo Nutricional)\n";
        echo "Ambiente: PHP " . PHP_VERSION . " | WordPress Test Harness\n";
        echo "=========================================================================\n";

        $suite = new AgroTracerS3T04TimelineManejoTest();
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
