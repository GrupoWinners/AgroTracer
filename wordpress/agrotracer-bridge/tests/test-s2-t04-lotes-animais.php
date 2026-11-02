<?php
/**
 * Automated Test Suite for Sprint 2 - Task S2-T04
 * Epic: [EP-S2] Sprint 2 — Animais, lotes e rastreabilidade temporal
 * Escopo: Páginas de Lotes e Animais (cadastro, listagem, filtros, badges de status e histórico) usando design system; ações visíveis sem hover.
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

    class AgroTracerS2T04LotesAnimaisTest extends TestCase {

        private string $templatesDir;
        private string $assetsDir;

        public function setUp(): void {
            parent::setUp();
            AgroTracer_WP_Test_Mock_State::reset();
            $this->templatesDir = dirname(__DIR__) . '/templates';
            $this->assetsDir = dirname(__DIR__) . '/assets';
        }

        /**
         * Teste 1: Verifica integridade sintática e existência dos templates da S2-T04
         */
        public function test_templates_exist_and_contain_required_identifiers(): void {
            $lotsFile = $this->templatesDir . '/lots.php';
            $modalsFile = $this->templatesDir . '/modals.php';

            $this->assertTrue(file_exists($lotsFile));
            $this->assertTrue(file_exists($modalsFile));

            $lotsHtml = file_get_contents($lotsFile);
            $modalsHtml = file_get_contents($modalsFile);

            // Sub-navegação em abas (Lotes vs Inventário de Animais)
            $this->assertStringContainsString('id="tab-btn-lotes"', $lotsHtml);
            $this->assertStringContainsString('id="tab-btn-animais"', $lotsHtml);
            $this->assertStringContainsString('id="view-lotes-container"', $lotsHtml);
            $this->assertStringContainsString('id="view-animais-container"', $lotsHtml);

            // Modais obrigatórios da S2-T04
            $this->assertStringContainsString('id="modal-create-lot"', $modalsHtml);
            $this->assertStringContainsString('id="modal-create-animal"', $modalsHtml);
            $this->assertStringContainsString('id="modal-animal-history"', $modalsHtml);
            $this->assertStringContainsString('id="modal-validation-error"', $modalsHtml);
        }

        /**
         * Teste 2: Aplicação rigorosa do Design System e Badges de Status
         */
        public function test_design_system_and_semantic_badges_applied(): void {
            $lotsHtml = file_get_contents($this->templatesDir . '/lots.php');
            $cssContent = file_get_contents($this->assetsDir . '/css/agrotracer-screens.css');

            // Badges semânticos no template
            $this->assertStringContainsString('class="agro-badge warning"', $lotsHtml);
            $this->assertStringContainsString('class="agro-badge info"', $lotsHtml);
            $this->assertStringContainsString('class="agro-badge success"', $lotsHtml);
            $this->assertStringContainsString('class="agro-badge neutral"', $lotsHtml);

            // Tokens do Design System declarados no CSS
            $this->assertStringContainsString('--agro-primary: #1b4332;', $cssContent);
            $this->assertStringContainsString('--agro-success-bg: #d1fae5;', $cssContent);
            $this->assertStringContainsString('--agro-danger-bg: #fee2e2;', $cssContent);
            $this->assertStringContainsString('--agro-warning-bg: #fef3c7;', $cssContent);
            $this->assertStringContainsString('--agro-info-bg: #dbeafe;', $cssContent);
        }

        /**
         * Teste 3: Cuidado de Engenharia — Sem dependência de hover para ações importantes
         */
        public function test_important_actions_are_visible_without_hover_dependency(): void {
            $lotsHtml = file_get_contents($this->templatesDir . '/lots.php');
            $cssContent = file_get_contents($this->assetsDir . '/css/agrotracer-screens.css');

            // Botões de ação com rótulo textual explícito no HTML
            $this->assertStringContainsString('+ Novo Lote', $lotsHtml);
            $this->assertStringContainsString('+ Cadastrar Animal', $lotsHtml);
            $this->assertStringContainsString('+ Associar Animais', $lotsHtml);
            $this->assertStringContainsString('<span>Ver Histórico</span>', $lotsHtml);
            $this->assertStringContainsString('<span>Desassociar</span>', $lotsHtml);
            $this->assertStringContainsString('<span>Editar Lote</span>', $lotsHtml);
            $this->assertStringContainsString('<span>+ Registrar Movimentação</span>', $lotsHtml);

            // Garantia de ausência de ocultação por hover no CSS
            $this->assertStringContainsString('.agro-table-actions', $cssContent);
            $this->assertStringContainsString('visibility: visible !important;', $cssContent);
            $this->assertStringContainsString('opacity: 1 !important;', $cssContent);

            // Nenhuma ação primária de linha deve usar exclusivamente agro-btn-icon-only sem texto
            $this->assertStringNotContainsString('class="agro-btn agro-btn-secondary agro-btn-icon-only" title="Ver Detalhes do Período"', $lotsHtml);
        }

        /**
         * Teste 4: Tratamento de Erros Esperados com Códigos Definidos (DoD)
         */
        public function test_expected_domain_error_codes_are_defined_and_mapped(): void {
            $modalsHtml = file_get_contents($this->templatesDir . '/modals.php');
            $jsContent = file_get_contents($this->assetsDir . '/js/agrotracer-screens.js');

            // Erro esperado para duplicidade de código de lote
            $this->assertStringContainsString('LOTE_CODIGO_DUPLICADO', $modalsHtml);
            $this->assertStringContainsString('LOTE_CODIGO_DUPLICADO', $jsContent);

            // Erro esperado para duplicidade de identificador animal (RN-05)
            $this->assertStringContainsString('ANIMAL_IDENTIFICADOR_DUPLICADO', $modalsHtml);
            $this->assertStringContainsString('ANIMAL_IDENTIFICADOR_DUPLICADO', $jsContent);

            // Erro esperado para conflito de associação temporal ativa (RN-06)
            $this->assertStringContainsString('ANIMAL_JA_ASSOCIADO_CONFLITO', $modalsHtml);
            $this->assertStringContainsString('ANIMAL_JA_ASSOCIADO_CONFLITO', $jsContent);
        }

        /**
         * Teste 5: Estrutura de Filtros de Lotes e Animais
         */
        public function test_filter_controls_are_present_for_lots_and_animals(): void {
            $lotsHtml = file_get_contents($this->templatesDir . '/lots.php');

            // Filtros de Lote
            $this->assertStringContainsString('id="search-lot-input"', $lotsHtml);
            $this->assertStringContainsString('id="filter-lot-farm"', $lotsHtml);
            $this->assertStringContainsString('id="filter-lot-status"', $lotsHtml);

            // Filtros do Inventário de Animais
            $this->assertStringContainsString('id="search-animals-input"', $lotsHtml);
            $this->assertStringContainsString('id="filter-animal-category"', $lotsHtml);
            $this->assertStringContainsString('id="filter-animal-status"', $lotsHtml);
            $this->assertStringContainsString('id="filter-animal-farm"', $lotsHtml);
            $this->assertStringContainsString('id="btn-clear-animal-filters"', $lotsHtml);
        }

        /**
         * Teste 6: Endpoints e Handlers REST da Bridge (FastAPI Proxy / Fallback)
         */
        public function test_bridge_controller_has_sprint2_handlers(): void {
            $bridge = AgroTracer_Bridge::get_instance();

            $this->assertTrue(method_exists($bridge, 'handle_create_lot'));
            $this->assertTrue(method_exists($bridge, 'handle_get_lots'));
            $this->assertTrue(method_exists($bridge, 'handle_create_animal'));
            $this->assertTrue(method_exists($bridge, 'handle_get_animals'));

            // Simula request de criação de lote
            $req = new \WP_REST_Request('POST', '/agrotracer/v1/lotes');
            $req->set_param('codigo_lote', 'LT-2026-TESTE');
            $req->set_param('fazenda_id', 1);

            $res = $bridge->handle_create_lot($req);
            $this->assertTrue($res !== null);
            $this->assertTrue(in_array($res->get_status(), [201, 200, 409], true));
        }
    }

    // Execução CLI Standalone
    if (php_sapi_name() === 'cli' && basename(__FILE__) === basename($_SERVER['SCRIPT_FILENAME'] ?? '')) {
        echo "=========================================================================\n";
        echo "AgroTracer Sprint 2 Test Suite: Task S2-T04 (Lotes, Animais & Zero Hover)\n";
        echo "Ambiente: PHP " . PHP_VERSION . " | WordPress Test Harness\n";
        echo "=========================================================================\n";

        $suite = new AgroTracerS2T04LotesAnimaisTest();
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
