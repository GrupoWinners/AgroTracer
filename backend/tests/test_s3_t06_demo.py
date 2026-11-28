"""Protege a proveniência do conjunto de demonstração distribuído."""

import json
from decimal import Decimal
from pathlib import Path

from app.services.parametro_rascunho_service import _validar_campos_fator


def test_demo_exclusivamente_sintetica_sem_atribuicao_institucional():
    arquivo = Path(__file__).parents[1] / "examples" / "parametros_demo.json"
    demo = json.loads(arquivo.read_text(encoding="utf-8"))
    assert demo["status"] == "RASCUNHO"
    assert demo["fatores"]
    assert "aprovado_por" not in demo
    assert "aprovado_em" not in demo
    for fator in demo["fatores"]:
        assert fator["source_type"] == "SYNTHETIC"
        assert fator["source_uri"] is None
        assert isinstance(fator["valor"], str)
        assert not {"IPCC", "EMBRAPA"}.intersection(
            fator["chave"].upper().split("_")
        )
        _validar_campos_fator(
            **dict(fator, valor=Decimal(fator["valor"]))
        )
