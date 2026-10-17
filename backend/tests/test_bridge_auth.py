from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from app.core.bridge_auth import verificar_hmac_requisicao
from app.core.hmac_protocol import (
    build_canonical_string,
    gerar_assinatura,
)


app_teste = FastAPI()

CHAVE_TESTE = b"segredo_ficticio_exclusivamente_para_testes"
AGORA_TESTE = 1800000000


@app_teste.post("/api/v1/fazendas")
async def cadastrar_fazenda_teste(request: Request):
    valido = await verificar_hmac_requisicao(
        request=request,
        chave=CHAVE_TESTE,
        cliente_redis=request.app.state.redis_cliente,
        agora=AGORA_TESTE,
    )

    if not valido:
        return JSONResponse(
            status_code=401,
            content={"autenticado": False},
        )

    return {"autenticado": True}


def criar_headers_assinados(corpo: bytes) -> dict[str, str]:
    timestamp = AGORA_TESTE
    nonce = "00112233445566778899aabbccddeeff"
    user_id = 42

    canonical = build_canonical_string(
        method="POST",
        path_with_query="/api/v1/fazendas?status=ativo",
        timestamp=timestamp,
        nonce=nonce,
        wp_user_id=user_id,
        body=corpo,
    )

    return {
        "X-AgroTracer-Signature": gerar_assinatura(
            canonical, CHAVE_TESTE
        ),
        "X-AgroTracer-Timestamp": str(timestamp),
        "X-AgroTracer-Nonce": nonce,
        "X-AgroTracer-User-Id": str(user_id),
        "X-Correlation-ID": (
            "123e4567-e89b-42d3-a456-426614174000"
        ),
    }


def test_requisicao_http_assinada():
    client = TestClient(app_teste)
    redis_falso = AsyncMock()
    redis_falso.set.return_value = True
    app_teste.state.redis_cliente = redis_falso
    corpo = b'{"nome":"Fazenda Azul"}'

    resposta = client.post(
        "/api/v1/fazendas?status=ativo",
        content=corpo,
        headers=criar_headers_assinados(corpo),
    )

    assert resposta.status_code == 200
    assert resposta.json() == {"autenticado": True}


def test_requisicao_http_corpo_alterado():
    client = TestClient(app_teste)
    redis_falso = AsyncMock()
    redis_falso.set.return_value = True
    app_teste.state.redis_cliente = redis_falso
    corpo_original = b'{"nome":"Fazenda Azul"}'
    corpo_alterado = b'{"nome":"Fazenda Verde"}'

    resposta = client.post(
        "/api/v1/fazendas?status=ativo",
        content=corpo_alterado,
        headers=criar_headers_assinados(corpo_original),
    )

    assert resposta.status_code == 401
    assert resposta.json() == {"autenticado": False}


def test_requisicao_http_nonce_repetido():
    client = TestClient(app_teste)

    redis_falso = AsyncMock()
    redis_falso.set.side_effect = [True, None]
    app_teste.state.redis_cliente = redis_falso

    corpo = b'{"nome":"Fazenda Azul"}'
    headers = criar_headers_assinados(corpo)

    primeira = client.post(
        "/api/v1/fazendas?status=ativo",
        content=corpo,
        headers=headers,
    )

    segunda = client.post(
        "/api/v1/fazendas?status=ativo",
        content=corpo,
        headers=headers,
    )

    assert primeira.status_code == 200
    assert segunda.status_code == 401

    assert redis_falso.set.await_count == 2
