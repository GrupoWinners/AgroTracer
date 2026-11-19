<?php
/**
 * Suite de Testes Automatizados — Task S6-T04 (QA Desktop 1366x768 e 1920x1080)
 *
 * Verifica invariantes de layout anti-clipping/overflow, navegação por hash,
 * breakpoints desktop e integridade do acervo de screenshots em Chrome e Edge.
 *
 * @package AgroTracerBridge\Tests
 */

declare(strict_types=1);

namespace AgroTracerBridge\Tests {
    require_once __DIR__ . '/bootstrap.php';

    use PHPUnit\Framework\TestCase;

    class AgroTracerS6T04DesktopQaTest extends TestCase {
        private string $pluginRoot;
        private string $repoRoot;

        public function setUp(): void {
            parent::setUp();
            $this->pluginRoot = dirname(__DIR__);
            $this->repoRoot = dirname(__DIR__, 3);
        }

        public function test_css_contains_kpi_and_screen_header_anti_clipping_rules(): void {
            $cssPath = $this->pluginRoot . '/assets/css/agrotracer-screens.css';
            $this->assertTrue(file_exists($cssPath), 'agrotracer-screens.css deve existir');

            $css = (string) file_get_contents($cssPath);

            // Regra anti-clipping de KPIs (corrigida na tela de Manejo em 1366x768 e 1920x1080)
            $this->assertMatchesRegularExpression('/\.agro-kpi-card\s*\{[^}]*min-width:\s*0;/s', $css);
            $this->assertMatchesRegularExpression('/#screen-manejo\s+\.agro-kpi-card\s*\{[^}]*flex-direction:\s*column;/s', $css);
            $this->assertMatchesRegularExpression('/#screen-manejo\s+\.agro-kpi-card\s*\{[^}]*gap:\s*6px;/s', $css);

            // Regras de cabeçalho de tela flexível e contêiner de ações sem compressão indevida
            $this->assertMatchesRegularExpression('/\.agro-screen-header\s*\{[^}]*display:\s*flex;/s', $css);
            $this->assertMatchesRegularExpression('/\.agro-screen-header\s*\{[^}]*flex-wrap:\s*wrap;/s', $css);
            $this->assertMatchesRegularExpression('/\.agro-screen-header\s*\{[^}]*justify-content:\s*space-between;/s', $css);
            $this->assertMatchesRegularExpression('/\.agro-screen-header-actions\s*\{[^}]*flex-shrink:\s*0;/s', $css);

            // Contêineres tabulares responsivos e breakpoints
            $this->assertStringContainsString('.agro-table-responsive', $css);
            $this->assertStringContainsString('@media (max-width: 1200px)', $css);
            $this->assertStringContainsString('@media (max-width: 900px)', $css);
        }

        public function test_js_registers_hashchange_navigation_listener(): void {
            $jsPath = $this->pluginRoot . '/assets/js/agrotracer-screens.js';
            $this->assertTrue(file_exists($jsPath), 'agrotracer-screens.js deve existir');

            $js = (string) file_get_contents($jsPath);
            $this->assertStringContainsString('const applyHashScreen =', $js);
            $this->assertStringContainsString("window.addEventListener('hashchange', applyHashScreen);", $js);
        }

        public function test_desktop_qa_screenshots_exist_and_are_valid_pngs(): void {
            $screenshotsDir = $this->repoRoot . '/docs/evidencias/sprint-6/screenshots';
            $this->assertTrue(is_dir($screenshotsDir), 'Diretório de screenshots da Sprint 6 deve existir');

            $expectedFiles = [
                'chrome-1366x768-dashboard.png',
                'chrome-1366x768-fazendas.png',
                'chrome-1366x768-lotes.png',
                'chrome-1366x768-animais.png',
                'chrome-1366x768-manejo.png',
                'chrome-1366x768-fechamento.png',
                'chrome-1366x768-certificados.png',
                'chrome-1366x768-publico.png',
                'chrome-1920x1080-dashboard.png',
                'chrome-1920x1080-fazendas.png',
                'chrome-1920x1080-lotes.png',
                'chrome-1920x1080-animais.png',
                'chrome-1920x1080-manejo.png',
                'chrome-1920x1080-fechamento.png',
                'chrome-1920x1080-certificados.png',
                'chrome-1920x1080-publico.png',
                'edge-1366x768-dashboard.png',
                'edge-1366x768-lotes.png',
                'edge-1366x768-manejo.png',
                'edge-1366x768-fechamento.png',
                'edge-1366x768-certificados.png',
                'edge-1366x768-publico.png',
                'edge-1920x1080-dashboard.png',
                'edge-1920x1080-lotes.png',
                'edge-1920x1080-manejo.png',
                'edge-1920x1080-fechamento.png',
                'edge-1920x1080-certificados.png',
                'edge-1920x1080-publico.png',
            ];

            $pngSignature = "\x89PNG\r\n\x1a\n";

            foreach ($expectedFiles as $filename) {
                $fullPath = $screenshotsDir . '/' . $filename;
                $this->assertTrue(file_exists($fullPath), "Screenshot ausente: {$filename}");
                $size = filesize($fullPath);
                $this->assertTrue($size !== false && $size > 10000, "Screenshot inválido ou vazio: {$filename}");

                $header = file_get_contents($fullPath, false, null, 0, 8);
                $this->assertSame($pngSignature, $header, "Assinatura PNG inválida em: {$filename}");
            }
        }
    }

    if (php_sapi_name() === 'cli' && basename(__FILE__) === basename($_SERVER['SCRIPT_FILENAME'] ?? '')) {
        echo "=========================================================================\n";
        echo "AgroTracer Sprint 6 Test Suite: Task S6-T04 (QA Desktop Chrome/Edge)\n";
        echo "Ambiente: PHP " . PHP_VERSION . " | WordPress Test Harness\n";
        echo "=========================================================================\n";

        $suite = new AgroTracerS6T04DesktopQaTest();
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
