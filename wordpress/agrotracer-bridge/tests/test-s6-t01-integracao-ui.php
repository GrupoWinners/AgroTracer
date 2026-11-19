<?php
/**
 * Automated Test Suite for Sprint 6 - Task S6-T01
 * Epic: [EP-S6] Sprint 6 — Integração, hardening, performance e UAT
 * Escopo: Revisar menus, breadcrumbs e estados; nenhum JSON cru / link quebrado;
 *         Design System aplicado.
 *
 * @package AgroTracerBridge\Tests
 */

declare(strict_types=1);

namespace AgroTracerBridge\Tests {

    require_once __DIR__ . '/bootstrap.php';
    require_once dirname(__DIR__) . '/includes/class-agrotracer-http-client.php';
    require_once dirname(__DIR__) . '/includes/class-agrotracer-shortcodes.php';
    require_once dirname(__DIR__) . '/includes/class-agrotracer-bridge.php';

    use AgroTracer_WP_Test_Mock_State;
    use AgroTracerBridge\Http\AgroTracer_Http_Client;
    use PHPUnit\Framework\TestCase;

    class AgroTracerS6T01IntegracaoUiTest extends TestCase {

        private string $templatesDir;
        private string $assetsDir;

        public function setUp(): void {
            parent::setUp();
            AgroTracer_WP_Test_Mock_State::reset();
            $this->templatesDir = dirname(__DIR__) . '/templates';
            $this->assetsDir    = dirname(__DIR__) . '/assets';
        }

        public function test_all_header_menu_items_have_screens_and_handlers(): void {
            $headerHtml = (string) file_get_contents($this->templatesDir . '/header.php');
            $pageHtml   = (string) file_get_contents($this->templatesDir . '/page-agrotracer.php');
            $certHtml   = (string) file_get_contents($this->templatesDir . '/certificados.php');
            $jsContent  = (string) file_get_contents($this->assetsDir . '/js/agrotracer-screens.js');

            $screens = ['dashboard', 'fazendas', 'lotes', 'manejo', 'fechamento', 'certificados'];
            foreach ($screens as $screen) {
                $this->assertStringContainsString('data-screen="' . $screen . '"', $headerHtml);
                $this->assertStringContainsString("'$screen'", $jsContent);
            }

            $this->assertStringContainsString("templates/certificados.php", $pageHtml);
            $this->assertStringContainsString('id="screen-certificados"', $certHtml);
            $this->assertStringContainsString('id="btn-header-notifications"', $headerHtml);
            $this->assertStringContainsString('id="agro-notifications-popover"', $headerHtml);
            $this->assertStringContainsString('id="btn-header-user-menu"', $headerHtml);
            $this->assertStringContainsString('id="agro-user-dropdown"', $headerHtml);
            $this->assertStringContainsString('function setupHeaderMenus()', $jsContent);
            $this->assertStringContainsString('function setupCertificadosModule()', $jsContent);
        }

        public function test_breadcrumbs_present_and_dynamically_updated(): void {
            $pageHtml   = (string) file_get_contents($this->templatesDir . '/page-agrotracer.php');
            $publicHtml = (string) file_get_contents($this->templatesDir . '/certificado-publico.php');
            $jsContent  = (string) file_get_contents($this->assetsDir . '/js/agrotracer-screens.js');

            $this->assertStringContainsString('id="agro-breadcrumb"', $pageHtml);
            $this->assertStringContainsString('aria-label="Breadcrumb"', $pageHtml);
            $this->assertStringContainsString('aria-label="Breadcrumb"', $publicHtml);
            $this->assertStringContainsString('function updateBreadcrumb()', $jsContent);
            $this->assertStringContainsString('updateBreadcrumb();', $jsContent);
        }

        public function test_no_broken_links_dead_buttons_or_native_alerts(): void {
            $dashboardHtml = (string) file_get_contents($this->templatesDir . '/dashboard.php');
            $farmsHtml     = (string) file_get_contents($this->templatesDir . '/farms.php');
            $lotsHtml      = (string) file_get_contents($this->templatesDir . '/lots.php');
            $jsContent     = (string) file_get_contents($this->assetsDir . '/js/agrotracer-screens.js');

            // Dashboard não possui mais botões mortos ou destinos trocados
            $this->assertStringContainsString("AgroTracer.openLotInFechamento(1)", $dashboardHtml);
            $this->assertStringContainsString("AgroTracer.switchScreen('manejo')", $dashboardHtml);
            $this->assertStringContainsString("AgroTracer.openLotInFechamento(2)", $dashboardHtml);
            $this->assertStringContainsString("AgroTracer.switchScreen('certificados')", $dashboardHtml);
            $this->assertStringNotContainsString("onclick=\"AgroTracer.switchScreen('lotes')\">\r\n                    Manejo", $dashboardHtml);

            // Links redundantes de volta à mesma tela foram corrigidos
            $this->assertStringNotContainsString('href="#fazendas"', $farmsHtml);
            $this->assertStringNotContainsString('href="#lotes"', $lotsHtml);

            // Zero alert() nativo do browser no engine frontend
            $this->assertStringNotContainsString('alert(', $jsContent);
        }

        public function test_all_five_ux_states_and_no_raw_json_exposure(): void {
            $farmsHtml = (string) file_get_contents($this->templatesDir . '/farms.php');
            $lotsHtml  = (string) file_get_contents($this->templatesDir . '/lots.php');
            $certHtml  = (string) file_get_contents($this->templatesDir . '/certificados.php');
            $pubHtml   = (string) file_get_contents($this->templatesDir . '/certificado-publico.php');
            $jsContent = (string) file_get_contents($this->assetsDir . '/js/agrotracer-screens.js');

            // Estados vazios e loading presentes
            $this->assertStringContainsString('id="farms-empty-state"', $farmsHtml);
            $this->assertStringContainsString('id="paddocks-empty-state"', $farmsHtml);
            $this->assertStringContainsString('id="lots-empty-state"', $lotsHtml);
            $this->assertStringContainsString('id="certificados-loading-state"', $certHtml);
            $this->assertStringContainsString('id="certificados-empty-state"', $certHtml);
            $this->assertStringContainsString('id="certificados-error-banner"', $certHtml);
            $this->assertStringContainsString('Verificando certificado...', $pubHtml);

            // Blindagem contra JSON cru e erros técnicos no JS e no PHP
            $this->assertStringContainsString('function formatSafeUiError(', $jsContent);
            $this->assertStringContainsString('function escapeHtml(', $jsContent);

            $rawPydantic = [
                'response' => ['code' => 422],
                'headers'  => [],
                'body'     => '{"detail":[{"loc":["body","numero_car"],"msg":"value is not valid"}]}',
            ];
            $normalized = AgroTracer_Http_Client::format_api_response($rawPydantic, '123e4567-e89b-42d3-a456-426614174000', time());
            $this->assertFalse($normalized['success']);
            $this->assertStringNotContainsString('{', $normalized['error']['message']);
            $this->assertStringNotContainsString('detail', $normalized['error']['message']);
        }

        public function test_design_system_tokens_applied_consistently(): void {
            $cssContent = (string) file_get_contents($this->assetsDir . '/css/agrotracer-screens.css');

            $requiredTokens = [
                '--agro-primary: #1b4332;',
                '--agro-primary-dark: #054a29;',
                '--agro-primary-hover: #03321b;',
                '--agro-bg-subtle: #f0f4f8;',
                '--agro-success-bg: #d1fae5;',
                '--agro-danger-bg: #fee2e2;',
                '--agro-warning-bg: #fef3c7;',
                '--agro-info-bg: #dbeafe;',
                '--agro-text-primary: #1f2937;',
                '--agro-border: #e5e7eb;',
            ];
            foreach ($requiredTokens as $token) {
                $this->assertStringContainsString($token, $cssContent);
            }

            // Alerta info corrigido para usar tokens info (não mais verde #f0fdf4)
            $this->assertStringContainsString("background-color: var(--agro-info-bg);", $cssContent);
            $this->assertStringContainsString('.agro-breadcrumb {', $cssContent);
            $this->assertStringContainsString('.agro-header-popover {', $cssContent);
        }
    }

    // Runner direto via PHP CLI
    if (php_sapi_name() === 'cli' && realpath($_SERVER['SCRIPT_FILENAME'] ?? '') === __FILE__) {
        echo "=========================================================================\n";
        echo "AgroTracer Sprint 6 Test Suite: Task S6-T01 (Integracao Menus/Estados)\n";
        echo "Ambiente: PHP " . PHP_VERSION . " | WordPress Test Harness\n";
        echo "=========================================================================\n";

        $suite   = new AgroTracerS6T01IntegracaoUiTest();
        $methods = array_filter(get_class_methods($suite), fn($m) => strpos($m, 'test_') === 0);
        $passed  = 0;
        $failed  = 0;
        $t0      = microtime(true);

        foreach ($methods as $method) {
            try {
                $suite->setUp();
                $suite->$method();
                echo " [PASS] {$method}\n";
                $passed++;
            } catch (\Throwable $e) {
                echo " [FAIL] {$method} -> " . $e->getMessage() . "\n";
                $failed++;
            }
        }

        $elapsed = round((microtime(true) - $t0) * 1000, 2);
        echo "-------------------------------------------------------------------------\n";
        echo "Resultado: {$passed} passaram | {$failed} falharam | Tempo: {$elapsed} ms\n";
        echo "=========================================================================\n";
        exit($failed > 0 ? 1 : 0);
    }
}
