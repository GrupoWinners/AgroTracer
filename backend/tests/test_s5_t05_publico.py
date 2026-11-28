import json
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.orm.attributes import flag_modified
from starlette.requests import Request

from app.core.bridge_dependency import exigir_usuario_wordpress
from app.main import app
from app.models.certificado import Certificado
from app.models.snapshot_fechamento import SnapshotFechamento
from app.services.certificacao_service import conteudo_snapshot, sha256_json
from app.services.certificado_publico_service import obter_ip_cliente
from test_s2_t01_api import ambiente_api  # noqa: F401
from test_s4_t02_fechamento import fechamento_api  # noqa: F401
from test_s5_t01_certificacao import emitir


def _emitir_e_preparar_publico(request):
    cenario = request.getfixturevalue("fechamento_api")
    emitido = emitir(cenario)
    assert emitido.status_code == 201, emitido.text
    cert = emitido.json()
    cliente = cenario[0]
    app.state.redis_cliente = AsyncMock()
    app.state.redis_cliente.eval.return_value = 1
    return cenario, cliente, cert


def test_consulta_publica_dto_minimizado_sem_autenticacao(request):
    cenario, cliente, cert = _emitir_e_preparar_publico(request)

    with cenario[1]() as db:
        obj = db.get(Certificado, cert["id"])
        snap = db.get(SnapshotFechamento, obj.snapshot_id)
        snap.entradas["email"] = "produtor@sigilo.example"
        snap.entradas["cpf"] = "123.456.789-00"
        snap.entradas["periodos"][0]["proveniencia"][0]["source_uri"] = (
            "https://interno.example/planilha-privada"
        )
        flag_modified(snap, "entradas")
        expected_sha = sha256_json(conteudo_snapshot(snap))
        obj.snapshot_sha256 = expected_sha
        db.commit()

    # Garante que a rota publica funciona sem exigir usuario WordPress/HMAC.
    app.dependency_overrides.pop(exigir_usuario_wordpress, None)
    resposta = cliente.get(
        "/api/v1/certificados/publico",
        params={"token": cert["token"]},
    )
    assert resposta.status_code == 200, resposta.text
    assert resposta.headers["cache-control"] == "no-store"
    assert resposta.headers["referrer-policy"] == "no-referrer"
    assert resposta.headers["x-robots-tag"] == "noindex, nofollow"

    corpo = resposta.json()
    # Identidade nao pode ser um campo do DTO; "42" pode ocorrer em hora/hash.
    assert set(corpo) == {
        "certificado_id", "lote_id", "status", "emitido_em", "versao_metodo",
        "versao_parametros", "source_types", "synthetic", "aviso_proveniencia",
        "data_abate", "numero_animais_abate", "resultados", "snapshot_sha256",
        "pdf_sha256",
    }
    assert corpo["certificado_id"] == cert["id"]
    assert corpo["lote_id"] == cert["lote_id"]
    assert corpo["status"] == "VALIDO"
    assert corpo["versao_metodo"] == "CARBONENGINE-MVP-1.0"
    assert corpo["versao_parametros"] == "S4-DEMO-1"
    assert corpo["source_types"] == ["SYNTHETIC"]
    assert corpo["synthetic"] is True
    assert "SYNTHETIC" in corpo["aviso_proveniencia"]
    assert corpo["data_abate"] == "2026-02-02"
    assert corpo["numero_animais_abate"] == 1
    assert corpo["snapshot_sha256"] == expected_sha
    assert corpo["pdf_sha256"] is None
    assert corpo["resultados"]["unidade_emissao"] == "kg CO2e"
    assert "carcaça" in corpo["resultados"]["unidade_intensidade"]
    assert corpo["resultados"]["emissao_total_kg_co2e"]
    assert corpo["resultados"]["intensidade_kg_co2e_kg"]

    texto = json.dumps(corpo, ensure_ascii=False)
    for proibido in (
        cert["token"],
        "token_hash",
        "idempotency_hash",
        "request_hash",
        "wordpress_user_id",
        "produtor_id",
        "Fazenda Fechamento",
        "Araguari",
        "CAR-FECH",
        "produtor@sigilo.example",
        "123.456.789-00",
        "planilha-privada",
        "source_uri",
        "BR-001",
    ):
        assert proibido not in texto


def test_consulta_publica_inclui_pdf_sha256_quando_gerado(request):
    cenario, cliente, cert = _emitir_e_preparar_publico(request)
    pdf_resp = cliente.get(f'/api/v1/certificados/{cert["id"]}/pdf')
    assert pdf_resp.status_code == 200

    resposta = cliente.get(
        "/api/v1/certificados/publico",
        params={"token": cert["token"]},
    )
    assert resposta.status_code == 200
    assert (
        resposta.json()["pdf_sha256"]
        == pdf_resp.headers["x-pdf-sha256"]
    )


def test_consulta_publica_certificado_revogado(request):
    cenario, cliente, cert = _emitir_e_preparar_publico(request)
    with cenario[1]() as db:
        obj = db.get(Certificado, cert["id"])
        obj.status = "REVOGADO"
        db.commit()

    resposta = cliente.get(
        "/api/v1/certificados/publico",
        params={"token": cert["token"]},
    )
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "REVOGADO"


@pytest.mark.parametrize("token", ["", "invalido", "A" * 43, "x" * 2048])
def test_consulta_publica_inexistente_generico_rn13(request, token):
    _, cliente, _ = _emitir_e_preparar_publico(request)
    resposta = cliente.get(
        "/api/v1/certificados/publico",
        params={"token": token},
    )
    assert resposta.status_code == 404
    erro = resposta.json()["error"]
    assert erro["code"] == "CERTIFICADO_NAO_ENCONTRADO"
    assert erro["message"] == "Certificado nao encontrado."
    app.state.redis_cliente.eval.assert_awaited_once()


def test_consulta_publica_respeita_rate_limit_e_falha_redis(request):
    _, cliente, cert = _emitir_e_preparar_publico(request)

    app.state.redis_cliente.eval.return_value = 31
    limitado = cliente.get(
        "/api/v1/certificados/publico",
        params={"token": cert["token"]},
    )
    assert limitado.status_code == 429
    assert limitado.json()["error"]["code"] == "LIMITE_CONSULTAS"

    app.state.redis_cliente.eval.side_effect = ConnectionError("redis down")
    indisponivel = cliente.get(
        "/api/v1/certificados/publico",
        params={"token": cert["token"]},
    )
    assert indisponivel.status_code == 503
    assert indisponivel.json()["error"]["code"] == "CONSULTA_INDISPONIVEL"

    delattr(app.state, "redis_cliente")
    sem_redis = cliente.get(
        "/api/v1/certificados/publico",
        params={"token": cert["token"]},
    )
    assert sem_redis.status_code == 503
    assert sem_redis.json()["error"]["code"] == "CONSULTA_INDISPONIVEL"


def test_consulta_publica_rejeita_snapshot_adulterado(request):
    cenario, cliente, cert = _emitir_e_preparar_publico(request)
    with cenario[1]() as db:
        obj = db.get(Certificado, cert["id"])
        obj.snapshot_sha256 = "0" * 64
        db.commit()

    resposta = cliente.get(
        "/api/v1/certificados/publico",
        params={"token": cert["token"]},
    )
    assert resposta.status_code == 409
    assert resposta.json()["error"]["code"] == "SNAPSHOT_INTEGRO_OBRIGATORIO"


def _fake_request(client_host: str, xff: str | None = None) -> Request:
    headers = []
    if xff is not None:
        headers.append((b"x-forwarded-for", xff.encode("ascii")))
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/api/v1/certificados/publico",
        "headers": headers,
        "client": (client_host, 54321),
    }
    return Request(scope)


def test_obter_ip_cliente_ignora_xff_sem_proxy_confiavel(monkeypatch):
    monkeypatch.delenv("AGROTRACER_TRUSTED_PROXIES", raising=False)
    req = _fake_request("203.0.113.10", "198.51.100.99")
    assert obter_ip_cliente(req) == "203.0.113.10"

    monkeypatch.setenv("AGROTRACER_TRUSTED_PROXIES", "127.0.0.1,10.0.0.0/8")
    req_spoof = _fake_request("203.0.113.10", "198.51.100.99")
    assert obter_ip_cliente(req_spoof) == "203.0.113.10"

    req_proxy = _fake_request("10.1.2.3", "198.51.100.77, 10.1.2.4")
    assert obter_ip_cliente(req_proxy) == "198.51.100.77"
