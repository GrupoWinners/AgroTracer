import pytest

from app.core.settings import obter_chave_bridge, obter_redis_url


def test_chave_bridge_configurada(monkeypatch):
    segredo = "chave_ficticia_para_testes_123456789"

    monkeypatch.setenv(
        "AGROTRACER_BRIDGE_SECRET",
        segredo,
    )

    assert obter_chave_bridge() == segredo.encode("ascii")


def test_chave_bridge_ausente(monkeypatch):
    monkeypatch.delenv(
        "AGROTRACER_BRIDGE_SECRET",
        raising=False,
    )

    with pytest.raises(RuntimeError):
        obter_chave_bridge()


def test_chave_bridge_curta(monkeypatch):
    monkeypatch.setenv(
        "AGROTRACER_BRIDGE_SECRET",
        "123456",
    )

    with pytest.raises(RuntimeError):
        obter_chave_bridge()


def test_redis_url_configurada(monkeypatch):
    url = "redis://127.0.0.1:6379/0"

    monkeypatch.setenv("AGROTRACER_REDIS_URL", url)

    assert obter_redis_url() == url


def test_redis_url_ausente(monkeypatch):
    monkeypatch.delenv(
        "AGROTRACER_REDIS_URL",
        raising=False,
    )

    with pytest.raises(RuntimeError):
        obter_redis_url()


def test_redis_url_invalida(monkeypatch):
    monkeypatch.setenv(
        "AGROTRACER_REDIS_URL",
        "http://localhost:6379",
    )

    with pytest.raises(RuntimeError):
        obter_redis_url()
