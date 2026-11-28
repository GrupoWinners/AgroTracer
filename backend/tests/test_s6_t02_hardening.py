import io
import json
import logging
from unittest.mock import AsyncMock

import pytest

from app.core.bridge_dependency import exigir_usuario_wordpress
from app.core.safe_logging import SafeFormatter
from app.main import app
from test_s2_t01_api import ambiente_api  # noqa: F401
from test_s4_t02_fechamento import fechamento_api  # noqa: F401
from test_s5_t01_certificacao import emitir
from test_s1_t05_crud_seguranca import _montar_headers_hmac


def test_hmac_duplicado_e_id_fora_bigint(request, monkeypatch):
    cliente, _ = request.getfixturevalue("ambiente_api")
    app.dependency_overrides.pop(exigir_usuario_wordpress)
    monkeypatch.setenv("AGROTRACER_BRIDGE_SECRET", "s" * 32)
    headers, _ = _montar_headers_hmac(chave=b"s" * 32)
    duplicados = list(headers.items()) + [("X-AgroTracer-User-Id", "99")]
    resp = cliente.get("/api/v1/fazendas", headers=duplicados)
    assert resp.status_code == 401
    headers, _ = _montar_headers_hmac(
        chave=b"s" * 32, wp_user_id=9223372036854775808,
    )
    assert cliente.get("/api/v1/fazendas", headers=headers).status_code == 401


def test_limite_privado_autenticado_e_falha_fechada(request, monkeypatch):
    cliente, _ = request.getfixturevalue("ambiente_api")
    app.dependency_overrides.pop(exigir_usuario_wordpress)
    monkeypatch.setenv("AGROTRACER_BRIDGE_SECRET", "s" * 32)
    redis = AsyncMock()
    redis.set.return_value = True
    redis.eval.side_effect = [120, 121, ConnectionError()]
    app.state.redis_cliente = redis
    for esperado in [200, 429, 503]:
        headers, _ = _montar_headers_hmac(chave=b"s" * 32)
        resp = cliente.get("/api/v1/fazendas", headers=headers)
        assert resp.status_code == esperado, resp.text


@pytest.mark.parametrize("metodo,caminho,corpo", [
    ("GET", "/fazendas/{fazenda}", None),
    ("PUT", "/fazendas/{fazenda}", {"nome": "Tentativa"}),
    ("GET", "/fazendas/{fazenda}/talhoes", None),
    ("POST", "/fazendas/{fazenda}/talhoes",
     {"identificador": "A", "area_hectares": "1"}),
    ("GET", "/lotes/{lote}", None),
    ("GET", "/lotes/{lote}/manejos", None),
    ("POST", "/lotes/{lote}/manejos", {
        "inicio": "2026-01-01", "fim": "2026-01-02",
        "tipo_dieta": "PASTAGEM", "parametro_set_id": 1,
    }),
    ("POST", "/lotes/{lote}/animais", {"animal_id": 1}),
    ("DELETE", "/lotes/{lote}/animais/1", None),
    ("GET", "/certificados/{certificado}/pdf", None),
])
def test_bola_todas_rotas_id(request, metodo, caminho, corpo):
    cenario = request.getfixturevalue("fechamento_api")
    certificado = emitir(cenario).json()["id"]
    from app.models.lote import Lote
    with cenario[1]() as db:
        fazenda = db.get(Lote, cenario[2]["lote"]).fazenda_id
    app.dependency_overrides[exigir_usuario_wordpress] = lambda: 999
    alvo = caminho.format(
        fazenda=fazenda, lote=cenario[2]["lote"], certificado=certificado,
    )
    resp = cenario[0].request(metodo, "/api/v1" + alvo, json=corpo)
    assert resp.status_code == 404, resp.text


def test_fechamento_certificacao_e_admin_nao_autorizados(request, monkeypatch):
    cenario = request.getfixturevalue("fechamento_api")
    app.dependency_overrides[exigir_usuario_wordpress] = lambda: 999
    assert emitir(cenario).status_code == 404
    from test_s4_t02_fechamento import enviar
    assert enviar(cenario).status_code == 404
    monkeypatch.setenv("AGROTRACER_ADMIN_WP_IDS", "42")
    resp = cenario[0].post(
        f'/api/v1/admin/parametro-sets/{cenario[2]["parametros"]}/ativar',
        json={"justificativa": "teste"},
    )
    assert resp.status_code == 403


def test_logs_nao_vazam_url_headers_corpo_ou_excecao(request):
    cliente, _ = request.getfixturevalue("ambiente_api")
    segredo = "TOKEN-SECRETO-email@example.com-123.456.789-00"
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(SafeFormatter())
    logger = logging.getLogger("agrotracer.http")
    logger.addHandler(handler)
    nivel = logger.level
    logger.setLevel(logging.INFO)
    try:
        redis = AsyncMock()
        redis.eval.return_value = 1
        app.state.redis_cliente = redis
        cliente.get("/api/v1/certificados/publico", params={"token": segredo})
        try:
            raise ValueError(segredo)
        except ValueError:
            logger.exception("URL=%s", segredo, extra={"password": segredo})
    finally:
        logger.removeHandler(handler)
        logger.setLevel(nivel)
    texto = stream.getvalue()
    assert segredo not in texto
    assert "email@example.com" not in texto
    registros = [json.loads(linha) for linha in texto.splitlines()]
    assert registros[0]["route"] == "/api/v1/certificados/publico"
    assert registros[0]["status"] == 404
    assert registros[-1]["event"] == "diagnostic_redacted"


def test_uvicorn_log_nao_vaza_query_ip_e_assinatura():
    record = logging.LogRecord(
        "uvicorn.access", logging.INFO, "", 0, '%s - "%s %s HTTP/%s" %d',
        ("192.0.2.1", "GET", "/?token=segredo", "1.1", 200), None,
    )
    texto = SafeFormatter().format(record)
    assert "segredo" not in texto
    assert "192.0.2.1" not in texto


def test_sec06_tokens_inexistentes_genericos_ate_bloqueio(request):
    cliente, _ = request.getfixturevalue("ambiente_api")
    redis = AsyncMock()
    redis.eval.side_effect = range(1, 32)
    app.state.redis_cliente = redis
    for numero in range(31):
        resposta = cliente.get(
            "/api/v1/certificados/publico",
            params={"token": f"inexistente-{numero}"},
        )
        assert resposta.status_code == (404 if numero < 30 else 429)
        if numero < 30:
            assert resposta.json()["error"]["message"] == (
                "Certificado nao encontrado."
            )
    assert redis.eval.await_count == 31
