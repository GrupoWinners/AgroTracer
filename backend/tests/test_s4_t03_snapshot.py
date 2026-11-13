"""S4-T03: snapshot fiel, imutabilidade logica e rollback."""

from decimal import Decimal

import pytest
from sqlalchemy import func, select

from app.models.fechamento_lote import FechamentoLote
from app.models.lote import Lote
from app.models.snapshot_fechamento import SnapshotFechamento
from app.services.carbon_engine import VERSAO_METODO

from test_s4_t02_fechamento import (  # noqa: F401
    enviar, fechamento_api,
)


def test_snapshot_criado_com_fechamento(request):
    fechamento_api = request.getfixturevalue("fechamento_api")
    _, sessao, ids = fechamento_api
    resposta = enviar(fechamento_api)
    assert resposta.status_code == 201, resposta.text
    with sessao() as db:
        snap = db.scalar(select(SnapshotFechamento).where(
            SnapshotFechamento.lote_id == ids["lote"],
        ))
        assert snap is not None
        assert snap.fechamento_id == resposta.json()["id"]
        assert snap.parametro_set_id == ids["parametros"]
        assert snap.versao_parametros == "S4-DEMO-1"
        assert snap.versao_metodo == VERSAO_METODO
        assert snap.entradas["periodos"][0]["numero_animais"] == 1
        assert snap.entradas["periodos"][0]["dias"] == 1
        assert snap.entradas["periodos"][0]["fatores"][
            "FE_BASE_DIETA"
        ] == "2.100000000000"
        assert Decimal(
            snap.resultados["emissao_total_kg_co2e"]
        ) == Decimal("2.1")
        assert Decimal(
            snap.resultados["intensidade_kg_co2e_kg"]
        ) > 0


def test_falha_snapshot_desfaz_fechamento(request, monkeypatch):
    fechamento_api = request.getfixturevalue("fechamento_api")
    _, sessao, ids = fechamento_api

    def falhar(*args, **kwargs):
        raise RuntimeError("erro proposital de snapshot")

    monkeypatch.setattr(
        "app.services.fechamento_service.persistir_snapshot_fechamento",
        falhar,
    )
    with pytest.raises(RuntimeError, match="erro proposital"):
        enviar(fechamento_api)
    with sessao() as db:
        assert db.get(Lote, ids["lote"]).status == "EM_MANEJO"
        assert db.scalar(select(func.count(FechamentoLote.id))) == 0
        assert db.scalar(select(func.count(SnapshotFechamento.id))) == 0


def test_sem_snapshot_quando_abate_invalido(request):
    fechamento_api = request.getfixturevalue("fechamento_api")
    _, sessao, ids = fechamento_api
    resposta = enviar(
        fechamento_api, numero_animais_abate=0,
    )
    assert resposta.status_code == 422
    with sessao() as db:
        assert db.get(Lote, ids["lote"]).status == "EM_MANEJO"
        assert db.scalar(select(func.count(SnapshotFechamento.id))) == 0
