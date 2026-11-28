<?php
/**
 * Automated Test Suite for Sprint 5 - Task S5-T04
 * Epic: [EP-S5] Sprint 5 — Certificado PDF, QR e consulta pública
 * Escopo: Fechar/emitir, loading, retry seguro e download.
 * Aceite objetivo: Clique duplo não duplica certificado.
 * Cuidado de engenharia: Idempotency-Key preservada.
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
    use AgroTracer_Http_Client_Alias;
    use AgroTracerBridge\Http\AgroTracer_Http_Client;
    use AgroTracer_WP_Test_Mock_State;
    use PHPUnit\Framework\TestCase;
    use WP_Error;

    class AgroTracerS5T04CertificacaoDownloadTest extends TestCase {

        private string $templatesDir;
        private string $assetsDir;

        public function setUp(): void {
            parent::setUp();
            AgroTracer_WP_Test_Mock_State::reset();
            $this->templatesDir = dirname(__DIR__) . '/templates';
            $this->assetsDir = dirname(__DIR__) . '/assets';
        }

        public function test_s5_t04_ui_components_and_retry_download_structure(): void {
            $fechamentoHtml = file_get_contents($this->templatesDir . '/fechamento.php');
            $modalsHtml     = file_get_contents($this->templatesDir . '/modals.php');
            $jsContent      = file_get_contents($this->assetsDir . '/js/agrotracer-screens.js');

            // Retry seguro & Idempotency-Key feedback
            $this->assertStringContainsString('id="btn-fechamento-retry-seguro"', $fechamentoHtml);
            $this->assertStringContainsString('id="fechamento-idempotency-status"', $fechamentoHtml);
            $this->assertStringContainsString('id="fechamento-idempotency-hint"', $fechamentoHtml);

            // Certificado emitido, token único e download PDF + retry
            $this->assertStringContainsString('id="certificado-resultado-card"', $fechamentoHtml);
            $this->assertStringContainsString('id="cert-res-snapshot-sha256"', $fechamentoHtml);
            $this->assertStringContainsString('id="cert-res-public-url"', $fechamentoHtml);
            $this->assertStringContainsString('id="btn-download-certificado-pdf"', $fechamentoHtml);
            $this->assertStringContainsString('id="spinner-download-pdf"', $fechamentoHtml);
            $this->assertStringContainsString('id="cert-pdf-error-box"', $fechamentoHtml);
            $this->assertStringContainsString('id="btn-retry-download-pdf"', $fechamentoHtml);

            // Modal menciona certificação atômica + Idempotency-Key
            $this->assertStringContainsString('Idempotency-Key', $modalsHtml);

            // JS envia Idempotency-Key para /certificar e baixa /pdf com trava dupla
            $this->assertStringContainsString('/certificar', $jsContent);
            $this->assertStringContainsString("'Idempotency-Key': idempotencyKey", $jsContent);
            $this->assertStringContainsString('getOrCreateIdempotencyKey', $jsContent);
            $this->assertStringContainsString('let isDownloadingPdf = false;', $jsContent);
            $this->assertStringContainsString('/certificados/${certId}/pdf', $jsContent);
            $this->assertStringContainsString('CERTIFICACAO_JA_PROCESSADA', $jsContent);
            $this->assertStringContainsString('IDEMPOTENCY_KEY_REUTILIZADA', $jsContent);
            $this->assertStringContainsString('PDF_INDISPONIVEL', $jsContent);
        }

        public function test_emitir_certificado_bridge_preserves_idempotency_key_and_strict_payload(): void {
            $bridge = AgroTracer_Bridge::get_instance();
            $this->assertTrue(method_exists($bridge, 'handle_emitir_certificado'));

            AgroTracer_WP_Test_Mock_State::$remote_handler = function (string $url, array $args) {
                $corrId = $args['headers']['X-Correlation-ID'] ?? 'corr-s5-t04';
                return [
                    'response' => ['code' => 201, 'message' => 'Created'],
                    'headers'  => ['x-correlation-id' => $corrId, 'cache-control' => 'no-store'],
                    'body'     => json_encode([
                        'id'              => 17,
                        'lote_id'         => 1,
                        'status'          => 'VALIDO',
                        'snapshot_sha256' => str_repeat('a', 64),
                        'token'           => 'tok_opaco_unico_teste_123',
                    ]),
                ];
            };

            $request = new \WP_REST_Request('POST', '/agrotracer/v1/lotes/1/certificar');
            $request->set_header('Idempotency-Key', 'agro-attempt-uuid-001');
            $request->set_param('lote_id', 1);
            $request->set_param('data_abate', '2026-06-01');
            $request->set_param('numero_animais_abate', 50);
            $request->set_param('peso_medio_abate_kg', '540.00');
            $request->set_param('rendimento_carcaca', '53.00');

            $response = $bridge->handle_emitir_certificado($request);
            $this->assertEquals(201, $response->get_status());

            $headers = $response->get_headers();
            $this->assertSame('no-store', $headers['Cache-Control']);
            $this->assertArrayHasKey('X-Correlation-ID', $headers);

            $data = $response->get_data();
            $this->assertEquals(17, $data['id']);
            $this->assertEquals('VALIDO', $data['status']);
            $this->assertEquals('tok_opaco_unico_teste_123', $data['token']);

            // Verifica requisição enviada ao FastAPI
            $sent = AgroTracer_WP_Test_Mock_State::$dispatched_requests[0];
            $this->assertStringContainsString('/api/v1/lotes/1/certificar', $sent['url']);
            $this->assertSame('agro-attempt-uuid-001', $sent['args']['headers']['Idempotency-Key']);
            $this->assertSame('42', $sent['args']['headers']['X-AgroTracer-Actor-ID']);
            $this->assertArrayHasKey('X-AgroTracer-Signature', $sent['args']['headers']);

            $sentBody = json_decode($sent['args']['body'], true);
            $this->assertArrayNotHasKey('produtor_id', $sentBody, 'FechamentoEntrada proibe campos extras');
            $this->assertSame('0.5300', $sentBody['rendimento_carcaca']);
            $this->assertSame('540.00', $sentBody['peso_medio_abate_kg']);
        }

        public function test_emitir_certificado_rejects_missing_or_invalid_idempotency_key(): void {
            $bridge = AgroTracer_Bridge::get_instance();

            $missingReq = new \WP_REST_Request('POST', '/agrotracer/v1/lotes/1/certificar');
            $missingReq->set_param('lote_id', 1);
            $missingReq->set_param('data_abate', '2026-06-01');
            $missingReq->set_param('numero_animais_abate', 50);
            $missingReq->set_param('peso_medio_abate_kg', '540.00');
            $missingReq->set_param('rendimento_carcaca', '0.5300');

            $missingRes = $bridge->handle_emitir_certificado($missingReq);
            $this->assertEquals(422, $missingRes->get_status());
            $this->assertSame('IDEMPOTENCY_KEY_INVALIDA', $missingRes->get_data()['error']['code']);
            $this->assertSame(0, count(AgroTracer_WP_Test_Mock_State::$dispatched_requests));

            $badReq = new \WP_REST_Request('POST', '/agrotracer/v1/lotes/1/certificar');
            $badReq->set_header('Idempotency-Key', 'chave com espaco');
            $badReq->set_param('lote_id', 1);
            $badRes = $bridge->handle_emitir_certificado($badReq);
            $this->assertEquals(422, $badRes->get_status());
            $this->assertSame(0, count(AgroTracer_WP_Test_Mock_State::$dispatched_requests));
        }

        public function test_emitir_certificado_safe_retry_on_503_and_409_controlled(): void {
            $bridge = AgroTracer_Bridge::get_instance();
            $callIndex = 0;

            AgroTracer_WP_Test_Mock_State::$remote_handler = function (string $url, array $args) use (&$callIndex) {
                $callIndex++;
                $corrId = $args['headers']['X-Correlation-ID'] ?? 'corr-retry';

                if ($callIndex === 1) {
                    return new WP_Error('http_request_failed', 'Timeout de rede');
                }
                if ($callIndex === 2) {
                    return [
                        'response' => ['code' => 409, 'message' => 'Conflict'],
                        'headers'  => ['x-correlation-id' => $corrId],
                        'body'     => json_encode([
                            'error' => [
                                'code'    => 'CERTIFICACAO_JA_PROCESSADA',
                                'message' => 'Chave ja utilizada.',
                            ],
                        ]),
                    ];
                }
                return [
                    'response' => ['code' => 409, 'message' => 'Conflict'],
                    'headers'  => ['x-correlation-id' => $corrId],
                    'body'     => json_encode([
                        'error' => [
                            'code'    => 'IDEMPOTENCY_KEY_REUTILIZADA',
                            'message' => 'Payload divergente.',
                        ],
                    ]),
                ];
            };

            $req = new \WP_REST_Request('POST', '/agrotracer/v1/lotes/1/certificar');
            $req->set_header('Idempotency-Key', 'retry-preserved-key-01');
            $req->set_param('lote_id', 1);
            $req->set_param('data_abate', '2026-06-01');
            $req->set_param('numero_animais_abate', 50);
            $req->set_param('peso_medio_abate_kg', '540.00');
            $req->set_param('rendimento_carcaca', '0.5300');

            // 1a tentativa: falha transiente 503 deve ser propagada (não mascarada)
            $res1 = $bridge->handle_emitir_certificado($req);
            $this->assertEquals(503, $res1->get_status());
            $this->assertSame('SERVICE_UNAVAILABLE', $res1->get_data()['error']['code']);

            // 2a tentativa (retry seguro com mesma Idempotency-Key): backend retorna 409 CERTIFICACAO_JA_PROCESSADA
            $res2 = $bridge->handle_emitir_certificado($req);
            $this->assertEquals(409, $res2->get_status());
            $this->assertSame('CERTIFICACAO_JA_PROCESSADA', $res2->get_data()['error']['code']);
            $this->assertSame(
                AgroTracer_WP_Test_Mock_State::$dispatched_requests[0]['args']['headers']['Idempotency-Key'],
                AgroTracer_WP_Test_Mock_State::$dispatched_requests[1]['args']['headers']['Idempotency-Key']
            );

            // 3a tentativa: 409 IDEMPOTENCY_KEY_REUTILIZADA
            $res3 = $bridge->handle_emitir_certificado($req);
            $this->assertEquals(409, $res3->get_status());
            $this->assertSame('IDEMPOTENCY_KEY_REUTILIZADA', $res3->get_data()['error']['code']);
        }

        public function test_download_certificado_pdf_binary_and_503_retry(): void {
            $bridge = AgroTracer_Bridge::get_instance();
            $this->assertTrue(method_exists($bridge, 'handle_download_certificado_pdf'));

            $fakePdf = "%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF";
            $expectedSha = hash('sha256', $fakePdf);
            $step = 0;

            AgroTracer_WP_Test_Mock_State::$remote_handler = function (string $url, array $args) use (&$step, $fakePdf, $expectedSha) {
                $step++;
                $corrId = $args['headers']['X-Correlation-ID'] ?? 'corr-pdf';

                if ($step === 1) {
                    return [
                        'response' => ['code' => 503, 'message' => 'Service Unavailable'],
                        'headers'  => ['x-correlation-id' => $corrId],
                        'body'     => json_encode([
                            'error' => [
                                'code'    => 'PDF_INDISPONIVEL',
                                'message' => 'PDF temporariamente indisponivel.',
                            ],
                        ]),
                    ];
                }

                return [
                    'response' => ['code' => 200, 'message' => 'OK'],
                    'headers'  => [
                        'content-type'        => 'application/pdf',
                        'content-disposition' => 'attachment; filename="certificado-17.pdf"',
                        'x-pdf-sha256'        => $expectedSha,
                        'cache-control'       => 'no-store',
                        'x-correlation-id'    => $corrId,
                    ],
                    'body'     => $fakePdf,
                ];
            };

            $req = new \WP_REST_Request('GET', '/agrotracer/v1/certificados/17/pdf');
            $req->set_param('certificado_id', 17);

            // 1a tentativa de download: 503 PDF_INDISPONIVEL propagado para permitir retry
            $errRes = $bridge->handle_download_certificado_pdf($req);
            $this->assertEquals(503, $errRes->get_status());
            $this->assertSame('PDF_INDISPONIVEL', $errRes->get_data()['error']['code']);

            // 2a tentativa: download binário 200 OK com integridade SHA-256
            $okRes = $bridge->handle_download_certificado_pdf($req);
            $this->assertEquals(200, $okRes->get_status());
            $this->assertSame($fakePdf, $okRes->get_data());
            $headers = $okRes->get_headers();
            $this->assertSame('application/pdf', $headers['Content-Type']);
            $this->assertSame($expectedSha, $headers['X-PDF-SHA256']);
            $this->assertSame('no-store', $headers['Cache-Control']);
            $this->assertSame('nosniff', $headers['X-Content-Type-Options']);

            // Verifica streaming binário sem JSON encoding via rest_pre_serve_request
            ob_start();
            $served = $bridge->serve_binary_pdf_response(false, $okRes, $req, null);
            $streamed = ob_get_clean();
            $this->assertTrue($served);
            $this->assertSame($fakePdf, $streamed);
        }

        public function test_http_client_extra_headers_cannot_override_hmac_headers(): void {
            AgroTracer_Http_Client::post(
                '/api/v1/lotes/1/certificar',
                ['data_abate' => '2026-06-01'],
                42,
                null,
                false,
                null,
                [
                    'Idempotency-Key'       => 'safe-key-123',
                    'X-AgroTracer-Actor-ID' => '999999',
                    'Content-Type'          => 'text/plain',
                ]
            );

            $sent = AgroTracer_WP_Test_Mock_State::$dispatched_requests[0]['args']['headers'];
            $this->assertSame('safe-key-123', $sent['Idempotency-Key']);
            $this->assertSame('42', $sent['X-AgroTracer-Actor-ID']);
            $this->assertSame('application/json', $sent['Content-Type']);
        }
    }

    if (php_sapi_name() === 'cli' && basename(__FILE__) === basename($_SERVER['SCRIPT_FILENAME'] ?? '')) {
        echo "=========================================================================\n";
        echo "AgroTracer Sprint 5 Test Suite: Task S5-T04 (Certificacao, Retry e PDF)\n";
        echo "Ambiente: PHP " . PHP_VERSION . " | WordPress Test Harness\n";
        echo "=========================================================================\n";

        $suite = new AgroTracerS5T04CertificacaoDownloadTest();
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
