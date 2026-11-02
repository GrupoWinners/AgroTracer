from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from uuid import UUID
from app.main import app


def test_health(monkeypatch):
    url = "redis://127.0.0.1:6379/0"
    monkeypatch.setenv("AGROTRACER_REDIS_URL", url)

    redis_falso = AsyncMock()

    with patch(
        "app.main.Redis.from_url",
        return_value=redis_falso,
    ):
        with TestClient(app) as client:
            resposta = client.get("/health")

            assert resposta.status_code == 200
            assert resposta.json() == {"status": "ok"}
            assert app.state.redis_cliente is redis_falso

    redis_falso.ping.assert_awaited_once()
    redis_falso.aclose.assert_awaited_once()


def test_api_sem_configuracao_redis(monkeypatch):
    monkeypatch.delenv(
        "AGROTRACER_REDIS_URL",
        raising=False,
    )

    with pytest.raises(RuntimeError):
        with TestClient(app):
            pass


def test_correlation_id_resposta_sucesso(monkeypatch):
    monkeypatch.setenv(
        "AGROTRACER_REDIS_URL",
        "redis://127.0.0.1:6379/0",
    )

    redis_falso = AsyncMock()

    with patch(
        "app.main.Redis.from_url",
        return_value=redis_falso,
    ):
        with TestClient(app) as client:
            correlation_id = (
                "123e4567-e89b-42d3-a456-426614174000"
            )

            resposta = client.get(
                "/health",
                headers={"X-Correlation-ID": correlation_id},
            )

            assert resposta.status_code == 200
            assert (
                resposta.headers["X-Correlation-ID"]
                == correlation_id
            )

            resposta_invalida = client.get(
                "/health",
                headers={"X-Correlation-ID": "invalido"},
            )

            novo_id = resposta_invalida.headers[
                "X-Correlation-ID"
            ]

            assert UUID(novo_id).version == 4
            assert novo_id != "invalido"
