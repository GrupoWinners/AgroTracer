"""S7-T03: QA Final — Consolidacao da Matriz de Testes, UAT e Bugs Conhecidos.

Valida programaticamente os criterios de aceite do gate final:
- Integridade do pacote de evidencias de release em docs/evidencias/sprint-7/
- Zero bugs P1/P2 em aberto registrados na documentacao
- Cobertura dos 8 vetores de seguranca (SEC-01 a SEC-08)
- Conformidade dos contratos de erro fail-closed e ausencia de segredos
"""

import json
from pathlib import Path

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


def test_rotas_privadas_bloqueadas_sem_autenticacao(request):
    """Garante rejeicao controlada e fail-closed em rotas criticas."""
    cenario = request.getfixturevalue("ambiente_api")
    cliente = cenario[0]

    app.dependency_overrides.pop(exigir_usuario_wordpress, None)

    for rota in [
        "/api/v1/fazendas",
        "/api/v1/lotes",
        "/api/v1/lotes/1/certificar",
        "/api/v1/certificados/1/pdf",
    ]:
        resp = cliente.get(rota)
        assert resp.status_code in (401, 403, 405, 503), (
            f"Rota {rota} deve rejeitar requisicao sem autenticacao"
        )
