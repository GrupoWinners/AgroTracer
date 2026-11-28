"""S3-T02: auditoria e protecao de rascunhos."""

import os
from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.models.auditoria_evento import AuditoriaEvento
from app.models.parametro_set import ParametroSet
from app.services.parametro_rascunho_service import (
    atualizar_fator_rascunho,
    atualizar_vigencia_rascunho,
    criar_fator_rascunho,
)
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
        with engine.connect() as conn:
            transacao = conn.begin()
            try:
                with Session(
                    bind=conn,
                    join_transaction_mode="create_savepoint",
                ) as db:
                    yield db
            finally:
                transacao.rollback()
    finally:
        engine.dispose()


def criar_conjunto(db):
    conjunto = ParametroSet(
        versao=f"S3-RASCUNHO-{uuid4().hex}",
        status="RASCUNHO",
        vigencia_inicio=date(2026, 1, 1),
    )
    db.add(conjunto)
    db.flush()
    return conjunto


def criar_fator(db, conjunto):
    return criar_fator_rascunho(
        db=db,
        parametro_set_id=conjunto.id,
        chave="FE_DEMO",
        unidade="kg CO2e/cabeca/dia",
        valor=Decimal("2.10"),
        source_type="SYNTHETIC",
        source_uri=None,
        wordpress_user_id=42,
        justificativa="Cadastro para teste de engenharia",
        correlation_id="s3-t02-rn16",
    )


def buscar_auditoria(db, entidade, entidade_id, acao):
    return db.scalar(
        select(AuditoriaEvento).where(
            AuditoriaEvento.entidade == entidade,
            AuditoriaEvento.entidade_id == entidade_id,
            AuditoriaEvento.acao == acao,
        )
    )


def test_criacao_fator_gera_auditoria(db_pg):
    conjunto = criar_conjunto(db_pg)
    fator = criar_fator(db_pg, conjunto)

    evento = buscar_auditoria(
        db_pg, "fator", fator.id, "CRIAR"
    )

    assert evento is not None
    assert evento.wordpress_user_id == 42
    assert evento.correlation_id == "s3-t02-rn16"
    assert evento.detalhes["source_type"] == "SYNTHETIC"
    assert evento.detalhes["justificativa"]


def test_edicao_fator_gera_antes_e_depois(db_pg):
    conjunto = criar_conjunto(db_pg)
    fator = criar_fator(db_pg, conjunto)

    atualizado = atualizar_fator_rascunho(
        db=db_pg,
        parametro_set_id=conjunto.id,
        fator_id=fator.id,
        chave="FE_DEMO",
        unidade="kg CO2e/cabeca/dia",
        valor=Decimal("1.40"),
        source_type="SYNTHETIC",
        source_uri=None,
        wordpress_user_id=42,
        justificativa="Revisao do fator didatico",
    )

    evento = buscar_auditoria(
        db_pg, "fator", fator.id, "ATUALIZAR"
    )

    assert atualizado.valor == Decimal("1.40")
    assert evento is not None
    assert Decimal(evento.detalhes["antes"]["valor"]) == (
        Decimal("2.10")
    )
    assert Decimal(evento.detalhes["depois"]["valor"]) == (
        Decimal("1.40")
    )


def test_alteracao_vigencia_gera_auditoria(db_pg):
    conjunto = criar_conjunto(db_pg)

    atualizar_vigencia_rascunho(
        db=db_pg,
        parametro_set_id=conjunto.id,
        vigencia_inicio=date(2026, 2, 1),
        vigencia_fim=date(2026, 12, 31),
        wordpress_user_id=42,
        justificativa="Ajuste do periodo de validade",
    )

    evento = buscar_auditoria(
        db_pg, "parametro_set", conjunto.id, "ATUALIZAR"
    )

    assert evento is not None
    assert evento.detalhes["antes"]["inicio"] == "2026-01-01"
    assert evento.detalhes["depois"]["inicio"] == "2026-02-01"


def test_versao_publicada_nao_pode_ser_editada(db_pg):
    conjunto = criar_conjunto(db_pg)
    fator = criar_fator(db_pg, conjunto)

    ativar_parametro_set(
        db=db_pg,
        parametro_set_id=conjunto.id,
        wordpress_user_id=42,
        justificativa="Aprovacao do conjunto de teste",
    )

    with pytest.raises(ErroParametro) as erro:
        atualizar_fator_rascunho(
            db=db_pg,
            parametro_set_id=conjunto.id,
            fator_id=fator.id,
            chave="FE_DEMO",
            unidade="kg CO2e/cabeca/dia",
            valor=Decimal("9.99"),
            source_type="SYNTHETIC",
            source_uri=None,
            wordpress_user_id=42,
            justificativa="Tentativa indevida",
        )

    assert erro.value.status_code == 409
    assert fator.valor == Decimal("2.10")


def test_fonte_nao_sintetica_exige_referencia(db_pg):
    conjunto = criar_conjunto(db_pg)

    with pytest.raises(ErroParametro) as erro:
        criar_fator_rascunho(
            db=db_pg,
            parametro_set_id=conjunto.id,
            chave="FE_TESTE",
            unidade="kg",
            valor=Decimal("1.0"),
            source_type="IPCC",
            source_uri=None,
            wordpress_user_id=42,
            justificativa="Teste de fonte obrigatoria",
        )

    assert erro.value.codigo == "FONTE_OBRIGATORIA"


def test_vigencia_invalida_retorna_422(db_pg):
    conjunto = criar_conjunto(db_pg)

    with pytest.raises(ErroParametro) as erro:
        atualizar_vigencia_rascunho(
            db=db_pg,
            parametro_set_id=conjunto.id,
            vigencia_inicio=date(2026, 12, 31),
            vigencia_fim=date(2026, 1, 1),
            wordpress_user_id=42,
            justificativa="Teste de data invalida",
        )

    assert erro.value.status_code == 422
    assert conjunto.vigencia_inicio == date(2026, 1, 1)
