import pytest
from app.core.bridge_dependency import exigir_usuario_wordpress
from app.main import app
from test_s1_t05_crud_seguranca import _montar_headers_hmac
from test_s2_t01_api import ambiente_api  # noqa: F401
from test_s4_t02_fechamento import fechamento_api  # noqa: F401


def test_uat_sessao_expirada_ou_sem_assinatura_retorna_401(request, monkeypatch):
    """
    Vetor 3 (Sessão Expirada / Credencial Inválida):
    Remove o mock de usuário da fixture e valida que requisições sem assinatura
    HMAC válida (ou com token expirado) retornam 401 com contrato estruturado.
    """
    cliente, _ = request.getfixturevalue("ambiente_api")
    app.dependency_overrides.pop(exigir_usuario_wordpress, None)
    monkeypatch.setenv("AGROTRACER_BRIDGE_SECRET", "s" * 32)

    resp_sem_header = cliente.get("/api/v1/fazendas")
    assert resp_sem_header.status_code == 401
    assert "error" in resp_sem_header.json()

    resp_token_invalido = cliente.get(
        "/api/v1/fazendas",
        headers={"Authorization": "Bearer sessao_expirada_invalida"},
    )
    assert resp_token_invalido.status_code == 401


def test_uat_dados_extremos_nao_geram_erro_500(request):
    """
    Vetor 4 (Dados Extremos / Boundary Testing):
    Envia string gigante (2.500 chars), payload XSS/SQLi e datas invertidas.
    A API deve rejeitar na camada de validação (400 ou 422) e jamais quebrar (500).
    """
    cenario = request.getfixturevalue("fechamento_api")
    cliente = cenario[0]
    lote_id = cenario[2]["lote"]

    payload_extremo = {
        "inicio": "2026-12-31",
        "fim": "2020-01-01",  # Data final anterior à inicial
        "tipo_dieta": "A" * 2500 + " <script>alert('xss')</script> ' OR 1=1 --",
        "parametro_set_id": -999999,
    }

    resp = cliente.post(f"/api/v1/lotes/{lote_id}/manejos", json=payload_extremo)

    assert resp.status_code in (400, 422), f"Falha de hardening! Veio {resp.status_code}: {resp.text}"
    assert "error" in resp.json() or "detail" in resp.json()


from unittest.mock import AsyncMock


def test_uat_clique_duplo_idempotencia_nonce_hmac(request, monkeypatch):
    """
    Vetor 1 (Clique Duplo / Replay de Requisição):
    Garante que o reenvio idêntico da mesma assinatura/nonce HMAC (simulando
    clique duplo ou interceptação de replay) seja bloqueado pela API.
    """
    cliente, _ = request.getfixturevalue("ambiente_api")
    app.dependency_overrides.pop(exigir_usuario_wordpress, None)
    monkeypatch.setenv("AGROTRACER_BRIDGE_SECRET", "s" * 32)

    # Simula o Redis aceitando o nonce inédito na 1ª chamada (True)
    # e rejeitando o replay duplicado na 2ª chamada (False)
    redis = AsyncMock()
    redis.set.side_effect = [True, False]
    redis.eval.return_value = 1
    app.state.redis_cliente = redis

    headers, _ = _montar_headers_hmac(chave=b"s" * 32)

    primeira = cliente.get("/api/v1/fazendas", headers=headers)
    segunda_duplicada = cliente.get("/api/v1/fazendas", headers=headers)

    assert primeira.status_code == 200
    assert segunda_duplicada.status_code == 401, "Replay de nonce HMAC deveria ser bloqueado!"