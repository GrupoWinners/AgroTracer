"""S4-T02: fechamento validado e transacao atomica."""

from datetime import date, datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy import func, select

from app.models.animal import Animal
from app.models.auditoria_evento import AuditoriaEvento
from app.models.fator import Fator
from app.models.fazenda import Fazenda
from app.models.fechamento_lote import FechamentoLote
from app.models.lote import Lote
from app.models.lote_animal import LoteAnimal
from app.models.manejo_nutricional import ManejoNutricional
from app.models.parametro_set import ParametroSet
from app.models.produtor import Produtor

from test_s2_t01_api import ambiente_api  # noqa: F401


@pytest.fixture
def fechamento_api(request):
    cliente, sessao = request.getfixturevalue("ambiente_api")
    with sessao() as db:
        produtor = Produtor(wordpress_user_id=42)
        fazenda = Fazenda(
            produtor=produtor, nome="Fazenda Fechamento",
            municipio="Araguari", uf="MG",
        )
        lote = Lote(
            fazenda=fazenda, codigo_lote="S4-FECHAMENTO",
            status="EM_MANEJO",
        )
        animal = Animal(
            produtor=produtor, identificador="S4-ANIMAL",
        )
        parametros = ParametroSet(
            versao="S4-DEMO-1",
            status="ATIVO",
            vigencia_inicio=date(2026, 1, 1),
            aprovado_por="wp:42",
            aprovado_em=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        db.add_all([lote, animal, parametros])
        db.flush()
        db.add_all([
            LoteAnimal(
                lote_id=lote.id, animal_id=animal.id,
                associado_em=datetime(
                    2026, 1, 1, tzinfo=timezone.utc,
                ),
            ),
            ManejoNutricional(
                lote_id=lote.id,
                parametro_set_id=parametros.id,
                inicio=date(2026, 2, 1),
                fim=date(2026, 2, 1),
                tipo_dieta="PASTAGEM",
            ),
        ])
        for chave, valor, unidade in [
            ("FE_BASE_DIETA:PASTAGEM", "2.10",
             "kg CO2e/cabeca/dia"),
            ("K_IDADE", "1", "1"),
            ("K_PASTAGEM", "1", "1"),
            ("K_SUPLEMENTACAO", "1", "1"),
        ]:
            db.add(Fator(
                parametro_set_id=parametros.id,
                chave=chave, unidade=unidade,
                valor=Decimal(valor), source_type="SYNTHETIC",
            ))
        ids = {"lote": lote.id, "parametros": parametros.id}
        db.commit()
    return cliente, sessao, ids


def enviar(cenario, **alteracoes):
    cliente, _, ids = cenario
    return cliente.post(
        f'/api/v1/lotes/{ids["lote"]}/fechamento',
        json={
            "data_abate": "2026-02-02",
            "numero_animais_abate": 1,
            "peso_medio_abate_kg": "540",
            "rendimento_carcaca": "0.53",
            **alteracoes,
        },
    )


def test_fechamento_valido_persiste_auditoria(fechamento_api):
    _, sessao, ids = fechamento_api
    resposta = enviar(fechamento_api)
    assert resposta.status_code == 201, resposta.text
    corpo = resposta.json()
    assert corpo["status_lote"] == "FECHADO"
    assert Decimal(corpo["emissao_total_kg_co2e"]) == Decimal("2.10")
    assert corpo["parametro_set_id"] == ids["parametros"]
    with sessao() as db:
        assert db.get(Lote, ids["lote"]).status == "FECHADO"
        assert db.scalar(select(func.count(FechamentoLote.id))) == 1
        evento = db.scalar(select(AuditoriaEvento).where(
            AuditoriaEvento.acao == "FECHAR_LOTE",
        ))
        assert evento is not None
        assert evento.entidade_id == corpo["id"]


def test_repetir_fechamento_retorna_409(fechamento_api):
    assert enviar(fechamento_api).status_code == 201
    resposta = enviar(fechamento_api)
    assert resposta.status_code == 409
    assert resposta.json()["error"]["code"] == "LOTE_ESTADO_INVALIDO"


@pytest.mark.parametrize("alteracoes", [
    {"numero_animais_abate": 0},
    {"numero_animais_abate": -1},
    {"peso_medio_abate_kg": "0"},
    {"peso_medio_abate_kg": "-1"},
    {"rendimento_carcaca": "0"},
    {"rendimento_carcaca": "-0.3"},
    {"rendimento_carcaca": "1.01"},
    {"data_abate": "2026-01-01"},
    {"wordpress_user_id": 84},
])
def test_rejeita_abate_invalido(fechamento_api, alteracoes):
    _, sessao, ids = fechamento_api
    resposta = enviar(fechamento_api, **alteracoes)
    assert resposta.status_code == 422
    with sessao() as db:
        assert db.get(Lote, ids["lote"]).status == "EM_MANEJO"
        assert db.scalar(select(func.count(FechamentoLote.id))) == 0


def test_falha_auditoria_faz_rollback(fechamento_api, monkeypatch):
    _, sessao, ids = fechamento_api

    def falhar(**kwargs):
        raise RuntimeError("auditoria indisponivel")

    monkeypatch.setattr(
        "app.services.fechamento_service.registrar_auditoria",
        falhar,
    )
    with pytest.raises(RuntimeError, match="auditoria indisponivel"):
        enviar(fechamento_api)
    with sessao() as db:
        assert db.get(Lote, ids["lote"]).status == "EM_MANEJO"
        assert db.scalar(select(func.count(FechamentoLote.id))) == 0


def test_lote_ausente_retorna_404(fechamento_api):
    cliente, _, _ = fechamento_api
    resposta = cliente.post(
        "/api/v1/lotes/999999/fechamento",
        json={
            "data_abate": "2026-02-02",
            "numero_animais_abate": 1,
            "peso_medio_abate_kg": "540",
            "rendimento_carcaca": "0.53",
        },
    )
    assert resposta.status_code == 404
