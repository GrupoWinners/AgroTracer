"""S4-T06: QA Gate da Sprint 4 — rotulagem SYNTHETIC e premissas da demo."""

import json
from datetime import date
from decimal import Decimal
from pathlib import Path

from app.services.carbon_engine import (
    VERSAO_METODO,
    FatoresVersionados,
    PeriodoCalculo,
    calcular_emissoes,
    calcular_intensidade,
)


RAIZ_REPO = Path(__file__).parents[2]


def test_telas_demo_rotulam_synthetic_e_limitacoes():
    """Garante rotulagem SYNTHETIC e aviso de limitacoes na UI."""
    fechamento = (
        RAIZ_REPO
        / "wordpress"
        / "agrotracer-bridge"
        / "templates"
        / "fechamento.php"
    ).read_text(encoding="utf-8")
    preview = (RAIZ_REPO / "wordpress" / "preview.html").read_text(
        encoding="utf-8"
    )

    assert 'data-source-type="SYNTHETIC"' in fechamento
    assert "[SYNTHETIC]" in fechamento
    assert "Premissas e Limitações" in fechamento
    assert "CARBONENGINE-MVP-1.0" in fechamento

    assert 'data-source-type="SYNTHETIC"' in preview
    assert "não representam inventário real nem fator oficial" in preview


def test_demo_calculo_deterministico_com_parametros_synthetic():
    """Valida a demo completa com fatores rotulados como SYNTHETIC."""
    demo_path = RAIZ_REPO / "backend" / "examples" / "parametros_demo.json"
    demo = json.loads(demo_path.read_text(encoding="utf-8"))
    valores = {f["chave"]: Decimal(f["valor"]) for f in demo["fatores"]}
    proveniencia = tuple(
        (f["chave"], f["unidade"], f["source_type"], str(f["source_uri"]))
        for f in demo["fatores"]
    )

    assert all(f["source_type"] == "SYNTHETIC" for f in demo["fatores"])
    assert "Sem validação científica" in demo["aviso"]

    fatores_p1 = FatoresVersionados(
        parametro_set_id=1,
        versao=demo["versao"],
        fe_base_dieta=valores["DEMO_FATOR_DIDATICO"],
        k_idade=Decimal("1"),
        k_pastagem=Decimal("1"),
        k_suplementacao=Decimal("1"),
        proveniencia=proveniencia,
    )
    fatores_p2 = FatoresVersionados(
        parametro_set_id=1,
        versao=demo["versao"],
        fe_base_dieta=Decimal("1.40"),
        k_idade=Decimal("1"),
        k_pastagem=Decimal("1"),
        k_suplementacao=Decimal("1"),
        proveniencia=proveniencia,
    )

    res = calcular_emissoes([
        PeriodoCalculo(date(2026, 1, 1), date(2026, 3, 31), 50, fatores_p1),
        PeriodoCalculo(date(2026, 4, 1), date(2026, 5, 30), 50, fatores_p2),
    ])
    intensidade = calcular_intensidade(
        res.total_kg_co2e, 50, Decimal("540"), Decimal("0.53")
    )

    assert res.versao_metodo == VERSAO_METODO
    assert res.total_kg_co2e == Decimal("13650")
    assert intensidade is not None
    assert intensidade.quantize(Decimal("0.001")) == Decimal("0.954")
    assert (
        calcular_intensidade(
            res.total_kg_co2e, 0, Decimal("540"), Decimal("0.53")
        )
        is None
    )
