from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.core.bridge_headers import (
    headers_obrigatorios_presentes,
    ler_headers_bridge,
    validar_headers_bridge,
)


app_teste = FastAPI()


@app_teste.get("/teste-headers")
def receber_headers(
    headers: dict[str, str | None] = Depends(ler_headers_bridge),
):
    return headers


def test_leitura_headers_bridge():
    client = TestClient(app_teste)

    resposta = client.get(
        "/teste-headers",
        headers={
            "X-AgroTracer-Signature": "assinatura-ficticia",
            "X-AgroTracer-Timestamp": "1800000000",
            "X-AgroTracer-Nonce": "00112233445566778899aabbccddeeff",
            "X-AgroTracer-User-Id": "42",
            "X-Correlation-ID": "123e4567-e89b-42d3-a456-426614174000",
        },
    )

    assert resposta.status_code == 200
    assert resposta.json()["timestamp"] == "1800000000"
    assert resposta.json()["user_id"] == "42"
    assert resposta.json()["signature"] == "assinatura-ficticia"


def test_headers_ausentes():
    client = TestClient(app_teste)

    resposta = client.get("/teste-headers")

    assert resposta.status_code == 200
    assert all(
        valor is None
        for valor in resposta.json().values()
    )


def test_headers_obrigatorios_presentes():
    headers = {
        "signature": "assinatura_teste",
        "timestamp": "1800000000",
        "nonce": "nonce_teste",
        "user_id": "42",
        "correlation_id": "correlation_teste",
    }

    assert headers_obrigatorios_presentes(headers) is True


def test_headers_obrigatorios_ausentes():
    headers = {
        "signature": "assinatura_teste",
        "timestamp": "1800000000",
        "nonce": "nonce_teste",
        "user_id": "42",
        "correlation_id": "correlation_teste",
    }

    for campo in headers:
        headers_incompletos = headers.copy()
        headers_incompletos[campo] = None

        assert headers_obrigatorios_presentes(
            headers_incompletos
        ) is False

    headers["signature"] = "   "

    assert headers_obrigatorios_presentes(headers) is False


def test_formato_headers_valido():
    agora = 1800000000

    headers = {
        "signature": "a" * 64,
        "timestamp": "1800000000",
        "nonce": "00112233445566778899aabbccddeeff",
        "user_id": "42",
        "correlation_id": "123e4567-e89b-42d3-a456-426614174000",
    }

    assert validar_headers_bridge(headers, agora) is True


def test_formato_headers_invalido():
    agora = 1800000000

    headers = {
        "signature": "a" * 64,
        "timestamp": "1800000000",
        "nonce": "00112233445566778899aabbccddeeff",
        "user_id": "42",
        "correlation_id": "123e4567-e89b-42d3-a456-426614174000",
    }

    alteracoes_invalidas = {
        "signature": "assinatura_errada",
        "timestamp": "abc",
        "nonce": "nonce_invalido",
        "user_id": "-1",
        "correlation_id": "identificador_invalido",
    }

    for campo, valor in alteracoes_invalidas.items():
        headers_alterados = headers.copy()
        headers_alterados[campo] = valor

        assert validar_headers_bridge(
            headers_alterados, agora
        ) is False
