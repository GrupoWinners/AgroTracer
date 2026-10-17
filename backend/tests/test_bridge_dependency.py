import time
from unittest.mock import AsyncMock

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.core.bridge_dependency import exigir_autenticacao_bridge
from app.core.hmac_protocol import (
    build_canonical_string,
    gerar_assinatura,
)
from app.core.bridge_errors import ErroBridge, tratar_erro_bridge
from redis.exceptions import ConnectionError as RedisConnectionError


app_teste = FastAPI()

app_teste.add_exception_handler(
    ErroBridge,
    tratar_erro_bridge,
)

SEGREDO_TESTE = "segredo_ficticio_com_mais_de_32_caracteres"


@app_teste.post(
    "/rota-protegida",
    dependencies=[Depends(exigir_autenticacao_bridge)],
)
async def rota_protegida():
    return {"autenticado": True}


def test_rota_bloqueia_sem_headers(monkeypatch):
    monkeypatch.setenv(
        "AGROTRACER_BRIDGE_SECRET",
        SEGREDO_TESTE,
    )

    app_teste.state.redis_cliente = AsyncMock()
    client = TestClient(app_teste)

    resposta = client.post("/rota-protegida")

    assert resposta.status_code == 401


def test_rota_bloqueia_sem_chave(monkeypatch):
    monkeypatch.delenv(
        "AGROTRACER_BRIDGE_SECRET",
        raising=False,
    )

    app_teste.state.redis_cliente = AsyncMock()
    client = TestClient(app_teste)

    resposta = client.post("/rota-protegida")

    assert resposta.status_code == 503


def test_rota_aceita_assinatura_valida(monkeypatch):
    monkeypatch.setenv(
        "AGROTRACER_BRIDGE_SECRET",
        SEGREDO_TESTE,
    )

    redis_falso = AsyncMock()
    redis_falso.set.return_value = True
    app_teste.state.redis_cliente = redis_falso

    timestamp = int(time.time())
    nonce = "00112233445566778899aabbccddeeff"
    corpo = b"{}"

    canonical = build_canonical_string(
        method="POST",
        path_with_query="/rota-protegida",
        timestamp=timestamp,
        nonce=nonce,
        wp_user_id=42,
        body=corpo,
    )

    assinatura = gerar_assinatura(
        canonical,
        SEGREDO_TESTE.encode("ascii"),
    )

    headers = {
        "X-AgroTracer-Signature": assinatura,
        "X-AgroTracer-Timestamp": str(timestamp),
        "X-AgroTracer-Nonce": nonce,
        "X-AgroTracer-User-Id": "42",
        "X-Correlation-ID": (
            "123e4567-e89b-42d3-a456-426614174000"
        ),
    }

    client = TestClient(app_teste)

    resposta = client.post(
        "/rota-protegida",
        content=corpo,
        headers=headers,
    )

    assert resposta.status_code == 200
    assert resposta.json() == {"autenticado": True}

    redis_falso.set.assert_awaited_once()


def test_envelope_erro_com_correlation_id(monkeypatch):
    monkeypatch.setenv(
        "AGROTRACER_BRIDGE_SECRET",
        SEGREDO_TESTE,
    )

    app_teste.state.redis_cliente = AsyncMock()
    client = TestClient(app_teste)

    correlation_id = "123e4567-e89b-42d3-a456-426614174000"

    resposta = client.post(
        "/rota-protegida",
        headers={
            "X-Correlation-ID": correlation_id,
        },
    )

    dados = resposta.json()

    assert resposta.status_code == 401
    assert dados["success"] is False
    assert dados["error"]["code"] == "AUTH_INVALID_REQUEST"
    assert dados["error"]["correlation_id"] == correlation_id
    assert dados["error"]["timestamp"].endswith("Z")
    assert resposta.headers["X-Correlation-ID"] == correlation_id


def test_rota_bloqueia_quando_redis_falha(monkeypatch):
    monkeypatch.setenv(
        "AGROTRACER_BRIDGE_SECRET",
        SEGREDO_TESTE,
    )

    redis_falso = AsyncMock()
    redis_falso.set.side_effect = RedisConnectionError(
        "Falha simulada no Redis"
    )
    app_teste.state.redis_cliente = redis_falso

    timestamp = int(time.time())
    nonce = "ffeeddccbbaa99887766554433221100"
    correlation_id = "123e4567-e89b-42d3-a456-426614174000"
    corpo = b"{}"

    canonical = build_canonical_string(
        method="POST",
        path_with_query="/rota-protegida",
        timestamp=timestamp,
        nonce=nonce,
        wp_user_id=42,
        body=corpo,
    )

    assinatura = gerar_assinatura(
        canonical,
        SEGREDO_TESTE.encode("ascii"),
    )

    headers = {
        "X-AgroTracer-Signature": assinatura,
        "X-AgroTracer-Timestamp": str(timestamp),
        "X-AgroTracer-Nonce": nonce,
        "X-AgroTracer-User-Id": "42",
        "X-Correlation-ID": correlation_id,
    }

    client = TestClient(app_teste)

    resposta = client.post(
        "/rota-protegida",
        content=corpo,
        headers=headers,
    )

    dados = resposta.json()

    assert resposta.status_code == 503
    assert dados["success"] is False
    assert (
        dados["error"]["code"]
        == "AUTH_SERVICE_UNAVAILABLE"
    )
    assert dados["error"]["correlation_id"] == correlation_id
    assert resposta.headers["X-Correlation-ID"] == correlation_id

    redis_falso.set.assert_awaited_once()


def test_assinatura_invalida_nao_registra_nonce(monkeypatch):
    monkeypatch.setenv(
        "AGROTRACER_BRIDGE_SECRET",
        SEGREDO_TESTE,
    )

    redis_falso = AsyncMock()
    app_teste.state.redis_cliente = redis_falso

    timestamp = int(time.time())
    nonce = "abcdef0123456789abcdef0123456789"
    correlation_id = "123e4567-e89b-42d3-a456-426614174000"

    corpo_original = b'{"nome":"Fazenda Azul"}'
    corpo_alterado = b'{"nome":"Fazenda Verde"}'

    canonical = build_canonical_string(
        method="POST",
        path_with_query="/rota-protegida",
        timestamp=timestamp,
        nonce=nonce,
        wp_user_id=42,
        body=corpo_original,
    )

    assinatura = gerar_assinatura(
        canonical,
        SEGREDO_TESTE.encode("ascii"),
    )

    headers = {
        "X-AgroTracer-Signature": assinatura,
        "X-AgroTracer-Timestamp": str(timestamp),
        "X-AgroTracer-Nonce": nonce,
        "X-AgroTracer-User-Id": "42",
        "X-Correlation-ID": correlation_id,
    }

    client = TestClient(app_teste)

    resposta = client.post(
        "/rota-protegida",
        content=corpo_alterado,
        headers=headers,
    )

    assert resposta.status_code == 401

    assert (
        resposta.json()["error"]["code"]
        == "AUTH_INVALID_REQUEST"
    )

    assert (
        resposta.headers["X-Correlation-ID"]
        == correlation_id
    )

    redis_falso.set.assert_not_awaited()
