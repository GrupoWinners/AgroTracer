<?php
/**
 * Automated Test Suite for Sprint 2 - Task S2-T05
 * Epic: [EP-S2] Sprint 2 — Animais, lotes e rastreabilidade temporal
 * Escopo: Timeline e formulários de associação e movimentação (alvo XOR: animal vs lote)
 * 
 * Critérios de Aceite:
 * 1. Conflito 409 exibido sem JSON técnico (mensagens claras ao produtor rural).
 * 2. Identidade NÃO vem de campos hidden (<input type="hidden" name="user_id|produtor_id"> é estritamente proibido).
 * 3. Validação XOR de alvo da movimentação (animal vs lote).
 * 4. Validação de rota de movimentação (origem != destino).
 * 5. Timeline cronológica com badges e rotas de rastreabilidade.
 * 6. Encerramento de associação temporal (RN-06) sem deleção física.
 *
 * @package AgroTracerBridge\Tests
 * @author João Vitor Santos de Souza (Losel / LoselSpt)
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

    class AgroTracerS2T05TimelineMovimentacaoTest extends TestCase {

        private string $templatesDir;
        private string $assetsDir;

        public function setUp(): void {
            parent::setUp();
            AgroTracer_WP_Test_Mock_State::reset();
            $this->templatesDir = dirname(__DIR__) . '/templates';
            $this->assetsDir = dirname(__DIR__) . '/assets';
        }

        /**
         * Teste 1: CUIDADO CRÍTICO DE ENGENHARIA — Zero hidden inputs de identidade
         * Garante que nenhum formulário carrega user_id ou produtor_id no DOM do cliente.
         */
        public function test_zero_hidden_identity_inputs_in_all_forms(): void {
            $lotsHtml = file_get_contents($this->templatesDir . '/lots.php');
            $modalsHtml = file_get_contents($this->templatesDir . '/modals.php');

            // Verifica ausência de hidden inputs de identidade em lots.php
            $this->assertFalse(
                (bool) preg_match('/<input[^>]+type=["\']hidden["\'][^>]+name=["\'](user_id|produtor_id)["\']/i', $lotsHtml),
                'Violação de segurança: Campo hidden de user_id/produtor_id encontrado em lots.php'
            );
            $this->assertFalse(
                (bool) preg_match('/<input[^>]+id=["\'](user_id|produtor_id)["\'][^>]+type=["\']hidden["\']/i', $lotsHtml),
                'Violação de segurança: Campo hidden com id user_id/produtor_id encontrado em lots.php'
            );

            // Verifica ausência de hidden inputs de identidade em modals.php
            $this->assertFalse(
                (bool) preg_match('/<input[^>]+type=["\']hidden["\'][^>]+name=["\'](user_id|produtor_id)["\']/i', $modalsHtml),
                'Violação de segurança: Campo hidden de user_id/produtor_id encontrado em modals.php'
            );
            $this->assertFalse(
                (bool) preg_match('/<input[^>]+id=["\'](user_id|produtor_id)["\'][^>]+type=["\']hidden["\']/i', $modalsHtml),
                'Violação de segurança: Campo hidden com id user_id/produtor_id encontrado em modals.php'
            );

            // Confirma ausência total de atributos name/id com identidade nos formulários
            $this->assertStringNotContainsString('name="user_id"', $modalsHtml);
            $this->assertStringNotContainsString('name="produtor_id"', $modalsHtml);
        }

        /**
         * Teste 2: Estrutura da Timeline de Movimentações e Rastreabilidade Visual
         */
        public function test_timeline_structure_and_visibility(): void {
            $lotsHtml = file_get_contents($this->templatesDir . '/lots.php');
            $cssContent = file_get_contents($this->assetsDir . '/css/agrotracer-screens.css');

            // Aba da Timeline no subnav
            $this->assertStringContainsString('id="tab-btn-timeline"', $lotsHtml);
            $this->assertStringContainsString('id="view-timeline-container"', $lotsHtml);

            // Card da Timeline contextual dentro de Lotes
            $this->assertStringContainsString('id="lot-movements-timeline-card"', $lotsHtml);
            $this->assertStringContainsString('id="lot-timeline-container"', $lotsHtml);
            $this->assertStringContainsString('id="global-timeline-container"', $lotsHtml);

            // Elementos de Timeline no Design System CSS
            $this->assertStringContainsString('.agro-timeline', $cssContent);
            $this->assertStringContainsString('.agro-timeline-item', $cssContent);
            $this->assertStringContainsString('.agro-timeline-dot', $cssContent);
            $this->assertStringContainsString('.agro-timeline-route', $cssContent);
        }

        /**
         * Teste 3: Formulário de Movimentação com Regra XOR de Alvo e Rota
         */
        public function test_movement_form_xor_target_and_route_validation(): void {
            $modalsHtml = file_get_contents($this->templatesDir . '/modals.php');
            $jsContent = file_get_contents($this->assetsDir . '/js/agrotracer-screens.js');

            // Modal de criação de movimentação existe
            $this->assertStringContainsString('id="modal-create-movement"', $modalsHtml);
            $this->assertStringContainsString('id="form-create-movement"', $modalsHtml);

            // Controles de Alvo XOR (Lote vs Animal)
            $this->assertStringContainsString('name="movement_target_type"', $modalsHtml);
            $this->assertStringContainsString('value="animal"', $modalsHtml);
            $this->assertStringContainsString('value="lote"', $modalsHtml);

            // Grupos condicionais XOR
            $this->assertStringContainsString('id="group-movement-lot"', $modalsHtml);
            $this->assertStringContainsString('id="group-movement-animal"', $modalsHtml);

            // Campos de Rota (Origem e Destino)
            $this->assertStringContainsString('id="movement-origin-paddock"', $modalsHtml);
            $this->assertStringContainsString('id="movement-dest-paddock"', $modalsHtml);

            // Lógica JS: Origem != Destino e XOR
            $this->assertStringContainsString('MOVIMENTACAO_ORIGEM_DESTINO_IGUAIS', $jsContent);
            $this->assertStringContainsString('Origem e destino não podem ser iguais', $modalsHtml);
        }

        /**
         * Teste 4: Tratamento de Conflito 409 Sem JSON Técnico
         */
        public function test_conflict_feedback_without_technical_json(): void {
            $modalsHtml = file_get_contents($this->templatesDir . '/modals.php');
            $jsContent = file_get_contents($this->assetsDir . '/js/agrotracer-screens.js');

            // Modal de Validação amigável
            $this->assertStringContainsString('id="modal-validation-error"', $modalsHtml);
            $this->assertStringContainsString('id="val-modal-title"', $modalsHtml);
            $this->assertStringContainsString('id="val-modal-description"', $modalsHtml);
            $this->assertStringContainsString('id="val-modal-conflict-box"', $modalsHtml);
            $this->assertStringContainsString('id="val-modal-conflict-code"', $modalsHtml);

            // Garantia de ausência de renderização de JSON bruto na interface do produtor
            $this->assertStringNotContainsString('{"detail":', $modalsHtml);
            $this->assertStringNotContainsString('{"error":', $modalsHtml);

            // O JavaScript trata respostas 409 e extrai mensagem legível, sem despejar payload JSON bruto
            $this->assertStringContainsString('openValidationErrorModal', $jsContent);
            $this->assertStringContainsString('MOVIMENTACAO_FORA_DE_ORDEM', $jsContent);
            $this->assertStringContainsString('ANIMAL_JA_ASSOCIADO_CONFLITO', $jsContent);
        }

        /**
         * Teste 5: Formulário de Encerramento de Associação Temporal (RN-06)
         */
        public function test_temporal_association_closure_form_rn06(): void {
            $modalsHtml = file_get_contents($this->templatesDir . '/modals.php');

            $this->assertStringContainsString('id="modal-disassociate-animal"', $modalsHtml);
            $this->assertStringContainsString('id="form-disassociate-animal"', $modalsHtml);
            $this->assertStringContainsString('id="disassociate-modal-animal-id"', $modalsHtml);
            $this->assertStringContainsString('id="disassociate-reason"', $modalsHtml);
            $this->assertStringContainsString('id="disassociate-datetime"', $modalsHtml);

            // O encerramento preserva histórico sem exclusão
            $this->assertStringContainsString('RN-06', $modalsHtml);
        }

        /**
         * Teste 6: Endpoints e Handlers REST da Bridge para Movimentações e Desassociação
         */
        public function test_bridge_controller_movement_and_disassociation_handlers(): void {
            $bridge = AgroTracer_Bridge::get_instance();

            $this->assertTrue(method_exists($bridge, 'handle_create_movement'));
            $this->assertTrue(method_exists($bridge, 'handle_get_movements'));
            $this->assertTrue(method_exists($bridge, 'handle_disassociate_animal'));

            // Caso A: Teste de violação de regra XOR (ambos alvos nulos) -> deve retornar 422
            $reqXorFail = new \WP_REST_Request('POST', '/agrotracer/v1/movimentacoes');
            $reqXorFail->set_param('origem_talhao_id', 1);
            $reqXorFail->set_param('destino_talhao_id', 2);
            $resXor = $bridge->handle_create_movement($reqXorFail);
            $this->assertSame(422, $resXor->get_status());
            $this->assertSame('MOVIMENTACAO_ALVO_INVALIDO', $resXor->get_data()['error']['code']);

            // Caso B: Teste de violação de rota (origem == destino) -> deve retornar 422
            $reqRouteFail = new \WP_REST_Request('POST', '/agrotracer/v1/movimentacoes');
            $reqRouteFail->set_param('animal_id', 10);
            $reqRouteFail->set_param('origem_talhao_id', 2);
            $reqRouteFail->set_param('destino_talhao_id', 2);
            $resRoute = $bridge->handle_create_movement($reqRouteFail);
            $this->assertSame(422, $resRoute->get_status());
            $this->assertSame('MOVIMENTACAO_ORIGEM_DESTINO_IGUAIS', $resRoute->get_data()['error']['code']);

            // Caso C: Movimentação válida (alvo animal, rota válida) -> sucesso (201 ou 200)
            $reqValid = new \WP_REST_Request('POST', '/agrotracer/v1/movimentacoes');
            $reqValid->set_param('animal_id', 1);
            $reqValid->set_param('origem_talhao_id', 1);
            $reqValid->set_param('destino_talhao_id', 2);
            $reqValid->set_param('data_movimentacao', '2026-10-30 08:30:00');
            $resValid = $bridge->handle_create_movement($reqValid);
            $this->assertTrue(in_array($resValid->get_status(), [201, 200], true));

            // Caso D: Listagem de movimentações -> 200
            $reqList = new \WP_REST_Request('GET', '/agrotracer/v1/movimentacoes');
            $resList = $bridge->handle_get_movements($reqList);
            $this->assertSame(200, $resList->get_status());
            $this->assertTrue(is_array($resList->get_data()));

            // Caso E: Desassociação temporal válida -> sucesso (200 ou 201)
            $reqDisassoc = new \WP_REST_Request('POST', '/agrotracer/v1/associacoes/encerrar');
            $reqDisassoc->set_param('animal_id', 1);
            $reqDisassoc->set_param('data_fim', '2026-10-30 08:45:00');
            $resDisassoc = $bridge->handle_disassociate_animal($reqDisassoc);
            $this->assertTrue(in_array($resDisassoc->get_status(), [200, 201], true));
        }
    }

    // Execução CLI Standalone
    if (php_sapi_name() === 'cli' && basename(__FILE__) === basename($_SERVER['SCRIPT_FILENAME'] ?? '')) {
        echo "=========================================================================\n";
        echo "AgroTracer Sprint 2 Test Suite: Task S2-T05 (Timeline & Movimentacao XOR)\n";
        echo "Ambiente: PHP " . PHP_VERSION . " | WordPress Test Harness\n";
        echo "=========================================================================\n";

        $suite = new AgroTracerS2T05TimelineMovimentacaoTest();
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
