
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_health_retorna_200():
    resposta = client.get("/health")

    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_openapi_disponivel():
    resposta = client.get("/openapi.json")

    assert resposta.status_code == 200
    assert "/health" in resposta.json()["paths"]
