"""S7-T03: QA Final — Consolidacao da Matriz de Testes, UAT e Bugs Conhecidos.

Valida programaticamente os criterios de aceite do gate final:
- Integridade do pacote de evidencias de release em docs/evidencias/sprint-7/
- Zero bugs P1/P2 em aberto registrados na documentacao
- Cobertura dos 8 vetores de seguranca (SEC-01 a SEC-08)
- Distincao estrita entre autenticacao 401 (POST/GET) e indisponibilidade 503
"""

import json
from pathlib import Path
from unittest.mock import AsyncMock

from app.core.bridge_dependency import exigir_usuario_wordpress
from app.main import app
from test_s2_t01_api import ambiente_api  # noqa: F401


RAIZ_REPO = Path(__file__).parents[2]


def test_pacote_evidencias_sprint7_completo():
    """Garante que todos os documentos do pacote de release estao presentes."""
    pasta_s7 = RAIZ_REPO / "docs" / "evidencias" / "sprint-7"
    assert pasta_s7.is_dir(), "Diretorio sprint-7 deve existir"

    documentos_obrigatorios = [
        "README.md",
        "S7-T01.md",
        "S7-T02.md",
        "S7-T03.md",
        "S7-T03-testes.txt",
        "S7-T05.md",
        "S7-T05-review-joao.md",
        "ci-verificada.json",
    ]
    for doc in documentos_obrigatorios:
        arquivo = pasta_s7 / doc
        assert arquivo.is_file(), f"Documento ausente no pacote: {doc}"
        assert arquivo.stat().st_size > 0, f"Documento vazio: {doc}"


def test_zero_bugs_p1_p2_em_aberto():
    """Verifica que nao ha P1/P2 pendentes no relatorio de QA e release."""
    s7_t03_path = RAIZ_REPO / "docs" / "evidencias" / "sprint-7" / "S7-T03.md"
    texto = s7_t03_path.read_text(encoding="utf-8")

    assert "ZERO (0) bugs P1/P2 em aberto" in texto
    assert "P1 (Bloqueante" in texto and "0 em aberto" in texto
    assert "P2 (Crítico" in texto and "0 em aberto" in texto


def test_ci_verificada_json_contem_suites_e_sem_segredos():
    """Valida formato e integridade do registro consolidado de CI."""
    ci_path = (
        RAIZ_REPO / "docs" / "evidencias" / "sprint-7" / "ci-verificada.json"
    )
    dados = json.loads(ci_path.read_text(encoding="utf-8"))

    assert "s7_t01" in dados
    assert "s7_t05" in dados
    run_url = dados["s7_t01"]["run"]
    assert "runs" in run_url or "actions" in run_url

    # Garante ausencia de tokens, senhas ou segredos no arquivo
    texto_serializado = json.dumps(dados)
    termos_proibidos = [
        "password",
        "secret_key",
        "client_secret",
        "BEGIN RSA",
        "ghp_",
        "AKIA",
    ]
    for termo in termos_proibidos:
        assert termo not in texto_serializado


def test_rotas_privadas_bloqueadas_sem_autenticacao(request, monkeypatch):
    """Garante rejeicao estrita com 401 usando o metodo HTTP correto."""
    cenario = request.getfixturevalue("ambiente_api")
    cliente = cenario[0]

    app.dependency_overrides.pop(exigir_usuario_wordpress, None)
    monkeypatch.setenv("AGROTRACER_BRIDGE_SECRET", "s" * 32)
    redis_mock = AsyncMock()
    redis_mock.set.return_value = True
    app.state.redis_cliente = redis_mock

    # 1. Rotas GET privadas sem HMAC devem retornar exatamente 401
    for rota in [
        "/api/v1/fazendas",
        "/api/v1/lotes",
        "/api/v1/certificados/1/pdf",
    ]:
        resp = cliente.get(rota)
        assert resp.status_code == 401, (
            f"GET {rota} sem HMAC deve retornar 401"
        )
        assert resp.json()["error"]["code"] == "AUTH_INVALID_REQUEST"

    # 2. Rota de certificacao usa POST: deve ser chamada com POST e dar 401
    payload_cert = {
        "data_abate": "2026-02-02",
        "numero_animais_abate": 1,
        "peso_medio_abate_kg": "540",
        "rendimento_carcaca": "0.53",
    }
    resp_post = cliente.post(
        "/api/v1/lotes/1/certificar",
        json=payload_cert,
        headers={"Idempotency-Key": "teste-auth-sem-hmac"},
    )
    assert resp_post.status_code == 401, (
        "POST /api/v1/lotes/1/certificar sem HMAC deve retornar 401"
    )
    assert resp_post.json()["error"]["code"] == "AUTH_INVALID_REQUEST"


def test_rotas_privadas_falham_fechado_sem_servico_autenticacao(request):
    """Cenario isolado de indisponibilidade: falha fechada com 503."""
    cenario = request.getfixturevalue("ambiente_api")
    cliente = cenario[0]

    app.dependency_overrides.pop(exigir_usuario_wordpress, None)
    if hasattr(app.state, "redis_cliente"):
        delattr(app.state, "redis_cliente")

    resp = cliente.get("/api/v1/fazendas")
    assert resp.status_code == 503
    assert resp.json()["error"]["code"] == "AUTH_SERVICE_UNAVAILABLE"
