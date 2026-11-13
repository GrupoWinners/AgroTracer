"""S4-T03: snapshot fiel, imutabilidade logica e rollback."""

from decimal import Decimal

import pytest
from sqlalchemy import func, select

from app.models.fechamento_lote import FechamentoLote
from app.models.lote import Lote
from app.models.snapshot_fechamento import SnapshotFechamento
from app.services.carbon_engine import VERSAO_METODO

from test_s2_t01_api import ambiente_api  # noqa: F401
from test_s4_t02_fechamento import enviar, fechamento_api  # noqa: F401


def test_snapshot_criado_com_fechamento(request):
    cenario = request.getfixturevalue("fechamento_api")
    _, sessao, ids = cenario
    resposta = enviar(cenario)
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
    cenario = request.getfixturevalue("fechamento_api")
    _, sessao, ids = cenario

    def falhar(*args, **kwargs):
        raise RuntimeError("erro proposital de snapshot")

    monkeypatch.setattr(
        "app.services.fechamento_service.persistir_snapshot_fechamento",
        falhar,
    )
    with pytest.raises(RuntimeError, match="erro proposital"):
        enviar(cenario)
    with sessao() as db:
        assert db.get(Lote, ids["lote"]).status == "EM_MANEJO"
        assert db.scalar(select(func.count(FechamentoLote.id))) == 0
        assert db.scalar(select(func.count(SnapshotFechamento.id))) == 0


def test_sem_snapshot_quando_abate_invalido(request):
    cenario = request.getfixturevalue("fechamento_api")
    _, sessao, ids = cenario
    resposta = enviar(
        cenario, numero_animais_abate=0,
    )
    assert resposta.status_code == 422
    with sessao() as db:
        assert db.get(Lote, ids["lote"]).status == "EM_MANEJO"
        assert db.scalar(select(func.count(SnapshotFechamento.id))) == 0


def test_novo_manejo_apos_fechamento_bloqueado(request):
    cenario = request.getfixturevalue("fechamento_api")
    cliente, _, ids = cenario
    assert enviar(cenario).status_code == 201
    resposta = cliente.post(
        f'/api/v1/lotes/{ids["lote"]}/manejos',
        json={
            "inicio": "2026-02-03",
            "fim": "2026-02-04",
            "tipo_dieta": "PASTAGEM",
            "parametro_set_id": ids["parametros"],
        },
    )
    assert resposta.status_code == 409
    assert resposta.json()["error"]["code"] == "LOTE_FECHADO"
