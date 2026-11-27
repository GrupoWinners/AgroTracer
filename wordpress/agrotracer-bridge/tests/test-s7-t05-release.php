<?php
declare(strict_types=1);

// Reusa somente stubs/classes do harness; seu runner nao roda via require.
require_once __DIR__ . '/test-s5-t05-consulta-publica.php';

use AgroTracerBridge\Http\AgroTracer_Http_Client;

function wp_get_environment_type(): string { return $GLOBALS['s7_env'] ?? 'production'; }
function exigir(bool $condicao, string $codigo): void {
    if (!$condicao) { throw new RuntimeException($codigo); }
}

$ssl = new ReflectionMethod(AgroTracer_Http_Client::class, 'should_verify_ssl');
exigir($ssl->invoke(null) === true, 'TLS_DEFAULT');
define('AGROTRACER_API_SSLVERIFY', false);
exigir($ssl->invoke(null) === true, 'TLS_NAO_PODE_DESLIGAR');

AgroTracer_WP_Test_Mock_State::$capabilities = ['publish_posts' => true];
try {
    AgroTracer_Http_Client::resolve_authorized_actor('valid_wp_nonce_token_123');
    throw new RuntimeException('AUTOR_NAO_DEVE_SER_PRODUTOR');
} catch (RuntimeException $erro) {
    exigir($erro->getCode() === 403, 'CAPABILITY_EXPLICITA');
}
AgroTracer_WP_Test_Mock_State::reset();
$bridge = AgroTracer_Bridge::get_instance();
AgroTracer_WP_Test_Mock_State::$remote_handler = static fn() => new WP_Error();
foreach (['handle_create_farm', 'handle_get_farms', 'handle_create_lot',
          'handle_get_lots', 'handle_create_animal', 'handle_create_manejo',
          'handle_get_manejos', 'handle_create_fechamento', 'handle_get_animals',
          'handle_get_parametros', 'handle_get_fechamentos'] as $metodo) {
    $req = new WP_REST_Request('POST');
    $req->set_param('lote_id', 1);
    $req->set_param('inicio', '2026-02-01');
    $req->set_param('fim', '2026-02-01');
    exigir($bridge->$metodo($req)->get_status() === 503, 'OFFLINE_' . $metodo);
}
exigir(!AgroTracer_Bridge::allow_offline_preview(), 'PREVIEW_DEFAULT');
define('AGROTRACER_OFFLINE_PREVIEW', true);
AgroTracer_WP_Test_Mock_State::$capabilities['manage_options'] = true;
exigir(!AgroTracer_Bridge::allow_offline_preview(), 'PREVIEW_PRODUCAO');
$GLOBALS['s7_env'] = 'local';
exigir(AgroTracer_Bridge::allow_offline_preview(), 'PREVIEW_LOCAL_ADMIN');
AgroTracer_WP_Test_Mock_State::$capabilities['manage_options'] = false;
exigir(!AgroTracer_Bridge::allow_offline_preview(), 'PREVIEW_PRODUTOR');
echo "S7-T05: TLS, capability, 11 falhas offline e preview restrito OK\n";
