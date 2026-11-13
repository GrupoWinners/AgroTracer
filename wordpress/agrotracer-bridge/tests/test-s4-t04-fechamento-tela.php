<?php
/**
 * Automated Test Suite for Sprint 4 - Task S4-T04
 * Epic: [EP-S4] Sprint 4 — Fechamento e CarbonEngine
 * Escopo: Tela de fechamento/abate com resumo, unidades e confirmação; prevenção de clique duplo; erro acionável.
 * Critérios de aceite:
 * 1. Campos e unidades claros (data AAAA-MM-DD, cabeças, kg vivo, % carcaça)
 * 2. Erro acionável com orientação de correção (422 associações parciais, abate superior, datas, 409 lote fechado)
 * 3. Sem submissão duplicada (botão desabilitado durante submit e trava de estado)
 * Cuidado de engenharia: Prevenção estrita de submissão dupla.
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
            public function get_headers(): array { return $this->headers; }
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

    class AgroTracerS4T04FechamentoTelaTest extends TestCase {

        private string $templatesDir;
        private string $assetsDir;

        public function setUp(): void {
            parent::setUp();
            AgroTracer_WP_Test_Mock_State::reset();
            $this->templatesDir = dirname(__DIR__) . '/templates';
            $this->assetsDir = dirname(__DIR__) . '/assets';
        }

        /**
         * Teste 1: Verifica existência e integridade dos templates e componentes de tela da S4-T04
         */
        public function test_templates_and_screen_structure_exist(): void {
            $fechamentoFile = $this->templatesDir . '/fechamento.php';
            $pageFile       = $this->templatesDir . '/page-agrotracer.php';
            $headerFile     = $this->templatesDir . '/header.php';
            $lotsFile       = $this->templatesDir . '/lots.php';
            $modalsFile     = $this->templatesDir . '/modals.php';

            $this->assertTrue(file_exists($fechamentoFile), 'Template fechamento.php deve existir');
            $this->assertTrue(file_exists($pageFile),       'Template page-agrotracer.php deve existir');

            $fechamentoHtml = file_get_contents($fechamentoFile);
            $pageHtml       = file_get_contents($pageFile);
            $headerHtml     = file_get_contents($headerFile);
            $lotsHtml       = file_get_contents($lotsFile);
            $modalsHtml     = file_get_contents($modalsFile);

            // 1. Inclusão no layout principal
            $this->assertStringContainsString('templates/fechamento.php', $pageHtml, 'page-agrotracer.php deve incluir fechamento.php');

            // 2. Container da tela principal de Fechamento
            $this->assertStringContainsString('id="screen-fechamento"', $fechamentoHtml);
            $this->assertStringContainsString('class="agro-screen"', $fechamentoHtml);

            // 3. Item de navegação no header
            $this->assertStringContainsString('data-screen="fechamento"', $headerHtml, 'header.php deve possuir botão data-screen="fechamento"');

            // 4. Ação de acesso rápido no detalhe de lotes
            $this->assertStringContainsString('id="btn-open-fechamento-from-lot"', $lotsHtml, 'lots.php deve possuir botão para fechar lote');

            // 5. Modal de confirmação com imutabilidade
            $this->assertStringContainsString('id="modal-confirm-fechamento"', $modalsHtml, 'modals.php deve possuir modal-confirm-fechamento');
        }

        /**
         * Teste 2: Critério de Aceite 1 — Campos e unidades claros
         */
        public function test_fields_and_units_clarity(): void {
            $fechamentoHtml = file_get_contents($this->templatesDir . '/fechamento.php');

            // Formulário de fechamento
            $this->assertStringContainsString('id="form-fechar-lote"', $fechamentoHtml);

            // 1. Data do abate com formato explícito
            $this->assertStringContainsString('id="fechamento-data-abate"', $fechamentoHtml);
            $this->assertStringContainsString('type="date"', $fechamentoHtml);
            $this->assertStringContainsString('AAAA-MM-DD', $fechamentoHtml);

            // 2. Quantidade de animais abatidos com unidade cab
            $this->assertStringContainsString('id="fechamento-animais-abate"', $fechamentoHtml);
            $this->assertStringContainsString('cabeças (cab)', $fechamentoHtml);

            // 3. Peso médio vivo com unidade kg
            $this->assertStringContainsString('id="fechamento-peso-medio"', $fechamentoHtml);
            $this->assertStringContainsString('kg / cabeça (kg vivo)', $fechamentoHtml);

            // 4. Rendimento de carcaça com percentual e fração decimal
            $this->assertStringContainsString('id="fechamento-rendimento"', $fechamentoHtml);
            $this->assertStringContainsString('rendimento-fração-preview', $fechamentoHtml);

            // 5. Pré-visualizações dinâmicas
            $this->assertStringContainsString('id="preview-peso-vivo-total"', $fechamentoHtml);
            $this->assertStringContainsString('id="preview-carcaca-total"', $fechamentoHtml);

            // 6. Unidades oficiais nos resultados (kg CO2e e kg CO2e / kg carcaça)
            $this->assertStringContainsString('kg CO₂e', $fechamentoHtml);
            $this->assertStringContainsString('kg CO₂e / kg carcaça', $fechamentoHtml);
        }

        /**
         * Teste 3: Critério de Aceite 2 — Erro acionável com orientação de correção
         */
        public function test_actionable_error_components_and_guidance(): void {
            $fechamentoHtml = file_get_contents($this->templatesDir . '/fechamento.php');
            $jsContent      = file_get_contents($this->assetsDir . '/js/agrotracer-screens.js');

            // 1. Banner semântico de erro acionável
            $this->assertStringContainsString('id="fechamento-actionable-error-banner"', $fechamentoHtml);
            $this->assertStringContainsString('id="fechamento-error-code-badge"', $fechamentoHtml);
            $this->assertStringContainsString('id="fechamento-error-title"', $fechamentoHtml);
            $this->assertStringContainsString('id="fechamento-error-message"', $fechamentoHtml);
            $this->assertStringContainsString('id="fechamento-error-action-guide"', $fechamentoHtml);
            $this->assertStringContainsString('id="btn-fechamento-error-action"', $fechamentoHtml);
            $this->assertStringContainsString('id="fechamento-error-correlation-id"', $fechamentoHtml);

            // 2. Mapeamento de orientações acionáveis em JS
            $this->assertStringContainsString('ABATE_SUPERIOR_AOS_ANIMAIS', $jsContent);
            $this->assertStringContainsString('ABATE_ANTERIOR_AO_MANEJO', $jsContent);
            $this->assertStringContainsString('ASSOCIACOES_PARCIAIS', $jsContent);
            $this->assertStringContainsString('MANEJO_OBRIGATORIO', $jsContent);
            $this->assertStringContainsString('LOTE_JA_FECHADO', $jsContent);
            $this->assertStringContainsString('PARAMETROS_NAO_PUBLICADOS', $jsContent);

            // 3. Instruções de ação direcionadas (redirecionamento ou auto-correção)
            $this->assertStringContainsString('Ir para Tela de Manejo', $jsContent);
            $this->assertStringContainsString('Ajustar para Total do Lote', $jsContent);
            $this->assertStringContainsString('Corrigir Data de Abate', $jsContent);
        }

        /**
         * Teste 4: Critério de Aceite 3 & Cuidado de Engenharia — Prevenção de dupla submissão
         */
        public function test_double_submission_prevention_engineering(): void {
            $fechamentoHtml = file_get_contents($this->templatesDir . '/fechamento.php');
            $jsContent      = file_get_contents($this->assetsDir . '/js/agrotracer-screens.js');
            $cssContent     = file_get_contents($this->assetsDir . '/css/agrotracer-screens.css');

            // 1. Botão de submit com spinner de loading
            $this->assertStringContainsString('id="btn-submit-fechamento"', $fechamentoHtml);
            $this->assertStringContainsString('id="spinner-fechamento"', $fechamentoHtml);
            $this->assertStringContainsString('class="agro-spinner"', $fechamentoHtml);

            // 2. Flag de controle estrito em JavaScript para bloquear duplo submit
            $this->assertStringContainsString('let isSubmitting = false;', $jsContent);
            $this->assertStringContainsString('if (isSubmitting) return;', $jsContent);
            $this->assertStringContainsString('isSubmitting = true;', $jsContent);
            $this->assertStringContainsString('btnSubmit.disabled = true;', $jsContent);

            // 3. Desabilitação e spinner de confirmação no modal
            $this->assertStringContainsString('btnDoConfirm.disabled = true;', $jsContent);
            $this->assertStringContainsString('Gravando snapshot...', $jsContent);

            // 4. Estilos CSS para botão desabilitado e animação de rotação
            $this->assertStringContainsString('.agro-spinner', $cssContent);
            $this->assertStringContainsString('@keyframes agro-spin', $cssContent);
            $this->assertStringContainsString('.agro-btn:disabled', $cssContent);
            $this->assertStringContainsString('pointer-events: none', $cssContent);
        }

        /**
         * Teste 5: Bridge REST Controller — Handlers e Contratos da S4-T04
         */
        public function test_bridge_controller_has_sprint4_fechamento_handlers(): void {
            $bridge = AgroTracer_Bridge::get_instance();

            $this->assertTrue(method_exists($bridge, 'handle_create_fechamento'), 'AgroTracer_Bridge deve implementar handle_create_fechamento');
            $this->assertTrue(method_exists($bridge, 'handle_get_fechamentos'),   'AgroTracer_Bridge deve implementar handle_get_fechamentos');

            // Configura mock handler remoto para simular responses do backend FastAPI HMAC
            AgroTracer_WP_Test_Mock_State::$remote_handler = function (string $url, array $args) {
                $corrId = $args['headers']['X-Correlation-ID'] ?? 'corr-test-s4-t04';
                $body   = json_decode($args['body'] ?? '{}', true);

                if (str_contains($url, '/fechamento')) {
                    if (isset($body['numero_animais_abate']) && $body['numero_animais_abate'] > 50) {
                        return [
                            'response' => ['code' => 422, 'message' => 'Unprocessable Entity'],
                            'headers'  => ['x-correlation-id' => $corrId],
                            'body'     => json_encode([
                                'error' => [
                                    'code'           => 'ABATE_SUPERIOR_AOS_ANIMAIS',
                                    'message'        => 'Quantidade abatida excede animais do ultimo manejo.',
                                    'correlation_id' => $corrId,
                                ]
                            ]),
                        ];
                    }

                    if (isset($body['data_abate']) && $body['data_abate'] < '2026-05-30') {
                        return [
                            'response' => ['code' => 422, 'message' => 'Unprocessable Entity'],
                            'headers'  => ['x-correlation-id' => $corrId],
                            'body'     => json_encode([
                                'error' => [
                                    'code'           => 'ABATE_ANTERIOR_AO_MANEJO',
                                    'message'        => 'Data de abate anterior ao fim do manejo.',
                                    'correlation_id' => $corrId,
                                ]
                            ]),
                        ];
                    }

                    if (str_contains($url, '/lotes/2/fechamento')) {
                        return [
                            'response' => ['code' => 409, 'message' => 'Conflict'],
                            'headers'  => ['x-correlation-id' => $corrId],
                            'body'     => json_encode([
                                'error' => [
                                    'code'           => 'LOTE_JA_FECHADO',
                                    'message'        => 'Lote ja possui fechamento.',
                                    'correlation_id' => $corrId,
                                ]
                            ]),
                        ];
                    }

                    return [
                        'response' => ['code' => 201, 'message' => 'Created'],
                        'headers'  => ['x-correlation-id' => $corrId],
                        'body'     => json_encode([
                            'id'                     => 101,
                            'lote_id'                => 1,
                            'status_lote'            => 'FECHADO',
                            'data_abate'             => $body['data_abate'] ?? '2026-06-01',
                            'numero_animais_abate'   => $body['numero_animais_abate'] ?? 50,
                            'parametro_set_id'       => 1,
                            'versao_metodo'          => 'CARBONENGINE-MVP-1.0',
                            'emissao_total_kg_co2e'  => '13650.000000000000000000',
                            'intensidade_kg_co2e_kg' => '0.953878406708595388',
                        ]),
                    ];
                }

                return [
                    'response' => ['code' => 200, 'message' => 'OK'],
                    'headers'  => ['x-correlation-id' => $corrId],
                    'body'     => json_encode(['data' => []]),
                ];
            };
            $requestSuccess = new \WP_REST_Request('POST', '/agrotracer/v1/fechamentos');
            $requestSuccess->set_param('lote_id', 1);
            $requestSuccess->set_param('data_abate', '2026-06-01');
            $requestSuccess->set_param('numero_animais_abate', 50);
            $requestSuccess->set_param('peso_medio_abate_kg', '540.00');
            $requestSuccess->set_param('rendimento_carcaca', '53.00'); // percentual convertido para 0.53

            $responseSuccess = $bridge->handle_create_fechamento($requestSuccess);
            $this->assertEquals(201, $responseSuccess->get_status());

            $dataSuccess = $responseSuccess->get_data();
            $this->assertEquals('FECHADO', $dataSuccess['status_lote']);
            $this->assertEquals('CARBONENGINE-MVP-1.0', $dataSuccess['versao_metodo']);
            $this->assertEquals(50, $dataSuccess['numero_animais_abate']);
            $this->assertStringContainsString('13650', (string) $dataSuccess['emissao_total_kg_co2e']);
            $this->assertStringContainsString('0.95', (string) $dataSuccess['intensidade_kg_co2e_kg']);

            // Headers de segurança e rastreabilidade
            $headers = $responseSuccess->get_headers();
            $this->assertArrayHasKey('X-Correlation-ID', $headers);
            $this->assertArrayHasKey('X-AgroTracer-Timestamp', $headers);

            // Cenário 2: Erro 422 - Animais de abate excedem o lote (Critério de Aceite 2)
            $requestExcesso = new \WP_REST_Request('POST', '/agrotracer/v1/fechamentos');
            $requestExcesso->set_param('lote_id', 1);
            $requestExcesso->set_param('data_abate', '2026-06-01');
            $requestExcesso->set_param('numero_animais_abate', 60); // 60 > 50
            $requestExcesso->set_param('peso_medio_abate_kg', '540.00');
            $requestExcesso->set_param('rendimento_carcaca', '0.53');

            $responseExcesso = $bridge->handle_create_fechamento($requestExcesso);
            $this->assertEquals(422, $responseExcesso->get_status());
            $dataExcesso = $responseExcesso->get_data();
            $this->assertEquals('ABATE_SUPERIOR_AOS_ANIMAIS', $dataExcesso['error']['code']);

            // Cenário 3: Erro 422 - Data de abate anterior ao fim do manejo
            $requestDataInvalida = new \WP_REST_Request('POST', '/agrotracer/v1/fechamentos');
            $requestDataInvalida->set_param('lote_id', 1);
            $requestDataInvalida->set_param('data_abate', '2026-01-01'); // 01/01 < 30/05
            $requestDataInvalida->set_param('numero_animais_abate', 50);
            $requestDataInvalida->set_param('peso_medio_abate_kg', '540.00');
            $requestDataInvalida->set_param('rendimento_carcaca', '0.53');

            $responseDataInvalida = $bridge->handle_create_fechamento($requestDataInvalida);
            $this->assertEquals(422, $responseDataInvalida->get_status());
            $this->assertEquals('ABATE_ANTERIOR_AO_MANEJO', $responseDataInvalida->get_data()['error']['code']);

            // Cenário 4: Erro 409 - Lote já fechado (irreversível)
            $requestJaFechado = new \WP_REST_Request('POST', '/agrotracer/v1/fechamentos');
            $requestJaFechado->set_param('lote_id', 2); // Lote 2 está mockado como FECHADO
            $requestJaFechado->set_param('data_abate', '2026-06-01');
            $requestJaFechado->set_param('numero_animais_abate', 45);
            $requestJaFechado->set_param('peso_medio_abate_kg', '540.00');
            $requestJaFechado->set_param('rendimento_carcaca', '0.53');

            $responseJaFechado = $bridge->handle_create_fechamento($requestJaFechado);
            $this->assertEquals(409, $responseJaFechado->get_status());
            $this->assertEquals('LOTE_JA_FECHADO', $responseJaFechado->get_data()['error']['code']);
        }
    }

    // Execução Standalone via CLI (PHPUnit Emulation Runner)
    if (php_sapi_name() === 'cli' && basename(__FILE__) === basename($_SERVER['SCRIPT_FILENAME'] ?? '')) {
        echo "=========================================================================\n";
        echo "AgroTracer Sprint 4 Test Suite: Task S4-T04 (Tela de Fechamento de Lote)\n";
        echo "Ambiente: PHP " . PHP_VERSION . " | WordPress Test Harness\n";
        echo "=========================================================================\n";

        $suite = new AgroTracerS4T04FechamentoTelaTest();
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
