"""Testes de ativacao versionada - PostgreSQL."""

import os
from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.models.auditoria_evento import AuditoriaEvento
from app.models.fator import Fator
from app.models.parametro_set import ParametroSet
from app.services.parametro_service import (
    ErroParametro,
    ativar_parametro_set,
)


@pytest.fixture
def db_pg():
    url = os.environ["AGROTRACER_TEST_DATABASE_URL"]
    assert make_url(url).database == "agrotracer_s2_t01_teste"

    engine = create_engine(url)

    try:
        with engine.connect() as conexao:
            transacao = conexao.begin()

            try:
                with Session(
                    bind=conexao,
                    join_transaction_mode="create_savepoint",
                ) as db:
                    yield db
            finally:
                transacao.rollback()
    finally:
        engine.dispose()


def criar_conjunto(db, com_fator=True):
    conjunto = ParametroSet(
        versao=f"TESTE-{uuid4().hex}",
        status="RASCUNHO",
        vigencia_inicio=date(2026, 1, 1),
    )
    db.add(conjunto)
    db.flush()

    if com_fator:
        db.add(
            Fator(
                parametro_set_id=conjunto.id,
                chave="FE_TESTE",
                unidade="kg CO2e/cabeca/dia",
                valor=Decimal("2.10"),
                source_type="SYNTHETIC",
            )
        )
        db.flush()

    return conjunto


def ativar(db, conjunto, justificativa="Teste de aprovacao"):
    return ativar_parametro_set(
        db=db,
        parametro_set_id=conjunto.id,
        wordpress_user_id=42,
        justificativa=justificativa,
        correlation_id="s3-t02-teste",
    )


def test_ativar_versao_com_auditoria(db_pg):
    conjunto = criar_conjunto(db_pg)

    resultado = ativar(db_pg, conjunto)

    assert resultado.status == "ATIVO"
    assert resultado.aprovado_por == "wp:42"
    assert resultado.aprovado_em is not None

    evento = db_pg.scalar(
        select(AuditoriaEvento).where(
            AuditoriaEvento.entidade == "parametro_set",
            AuditoriaEvento.entidade_id == conjunto.id,
            AuditoriaEvento.acao == "ATIVAR",
        )
    )

    assert evento is not None
    assert evento.wordpress_user_id == 42
    assert evento.correlation_id == "s3-t02-teste"
    assert evento.detalhes["justificativa"] == (
        "Teste de aprovacao"
    )


def test_nova_versao_inativa_anterior(db_pg):
    primeiro = criar_conjunto(db_pg)
    segundo = criar_conjunto(db_pg)

    ativar(db_pg, primeiro)
    ativar(db_pg, segundo)

    assert primeiro.status == "INATIVO"
    assert segundo.status == "ATIVO"

    auditoria = db_pg.scalar(
        select(AuditoriaEvento).where(
            AuditoriaEvento.entidade_id == primeiro.id,
            AuditoriaEvento.entidade == "parametro_set",
            AuditoriaEvento.acao == "INATIVAR",
        )
    )

    assert auditoria is not None
    assert auditoria.detalhes["substituido_por_id"] == (
        segundo.id
    )


def test_nao_ativar_versao_sem_fatores(db_pg):
    conjunto = criar_conjunto(db_pg, com_fator=False)

    with pytest.raises(ErroParametro) as erro:
        ativar(db_pg, conjunto)

    assert erro.value.status_code == 422
    assert erro.value.codigo == "PARAMETRO_SET_SEM_FATORES"
    assert conjunto.status == "RASCUNHO"


def test_justificativa_obrigatoria(db_pg):
    conjunto = criar_conjunto(db_pg)

    with pytest.raises(ErroParametro) as erro:
        ativar(db_pg, conjunto, justificativa="  ")

    assert erro.value.status_code == 422
    assert conjunto.status == "RASCUNHO"


def test_nao_reativar_historico(db_pg):
    primeiro = criar_conjunto(db_pg)
    segundo = criar_conjunto(db_pg)

    ativar(db_pg, primeiro)
    ativar(db_pg, segundo)

    with pytest.raises(ErroParametro) as erro:
        ativar(db_pg, primeiro)

    assert erro.value.status_code == 409
    assert erro.value.codigo == "PARAMETRO_SET_IMUTAVEL"


def test_nao_ativar_duas_vezes(db_pg):
    conjunto = criar_conjunto(db_pg)
    ativar(db_pg, conjunto)

    with pytest.raises(ErroParametro) as erro:
        ativar(db_pg, conjunto)

    assert erro.value.status_code == 409
    assert erro.value.codigo == "PARAMETRO_SET_JA_ATIVO"
