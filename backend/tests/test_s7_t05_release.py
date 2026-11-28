import pytest
from fastapi.testclient import TestClient

from app.core.bridge_errors import ErroBridge
from app.main import app
from app.services.certificado_publico_service import obter_ip_cliente
from test_s5_t05_publico import _fake_request


@pytest.mark.parametrize("rede", ["0.0.0.0/0", "::/0", "invalido"])
def test_proxy_irrestrito_ou_invalido_falha_fechado(monkeypatch, rede):
    monkeypatch.setenv("AGROTRACER_TRUSTED_PROXIES", rede)
    with pytest.raises(ErroBridge) as erro:
        obter_ip_cliente(_fake_request("10.0.0.1", "198.51.100.1"))
    assert erro.value.status_code == 503


def test_xff_so_confia_no_peer_e_cadeia_definidos(monkeypatch):
    monkeypatch.setenv("AGROTRACER_TRUSTED_PROXIES", "10.1.1.1/32")
    req = _fake_request("203.0.113.1", "1.2.3.4")
    assert obter_ip_cliente(req) == "203.0.113.1"
    req = _fake_request("10.1.1.1", "1.2.3.4, 203.0.113.1")
    assert obter_ip_cliente(req) == "203.0.113.1"


def test_debug_desligado_e_cors_nao_libera_origem_arbitraria():
    assert app.debug is False
    cliente = TestClient(app)
    resp = cliente.options("/api/v1/fazendas", headers={
        "Origin": "https://nao-autorizado.example",
        "Access-Control-Request-Method": "POST",
    })
    assert "access-control-allow-origin" not in resp.headers
    assert "access-control-allow-credentials" not in resp.headers
