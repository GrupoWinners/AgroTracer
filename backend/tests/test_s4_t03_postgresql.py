"""S4-T03: triggers PostgreSQL impedem snapshot e fechamento mutaveis."""

import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError


@pytest.fixture
def conexao_pg():
    url = os.getenv("AGROTRACER_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Banco PostgreSQL de testes nao configurado")
    if make_url(url).database != "agrotracer_s2_t01_teste":
        pytest.fail("Exige banco descartavel agrotracer_s2_t01_teste")
    engine = create_engine(url)
    try:
        with engine.connect() as conn:
            transacao = conn.begin()
            try:
                yield conn
            finally:
                transacao.rollback()
    finally:
        engine.dispose()


def test_triggers_de_integridade_presentes(conexao_pg):
    nomes = set(conexao_pg.scalars(text("""
        SELECT tgname FROM pg_trigger
        WHERE tgrelid IN (
            'snapshots_fechamento'::regclass,
            'fechamentos_lote'::regclass
        ) AND NOT tgisinternal
    """)).all())
    assert {
        "trg_snapshot_imutavel",
        "trg_fechamento_imutavel",
        "trg_fechamento_snapshot",
    } <= nomes


def test_fechamento_sem_snapshot_nao_confirma(conexao_pg):
    # Uma FK verdadeira e criada em savepoint e nunca confirmada.
    # A verificacao da restricao adiada e forcada antes do rollback.
    ids = conexao_pg.execute(text("""
        SELECT l.id AS lote_id, p.id AS parametro_set_id
        FROM lotes l CROSS JOIN parametro_sets p
        LIMIT 1
    """)).first()
    if ids is None:
        pytest.skip("Nao ha dados de teste para este check")

    with pytest.raises(DBAPIError):
        with conexao_pg.begin_nested():
            conexao_pg.execute(text("""
                INSERT INTO fechamentos_lote (
                    lote_id, parametro_set_id, versao_metodo,
                    data_abate, numero_animais_abate,
                    peso_medio_abate_kg, rendimento_carcaca,
                    emissao_total_kg_co2e, intensidade_kg_co2e_kg
                ) VALUES (
                    :lote_id, :parametro_set_id, 'TESTE',
                    '2026-11-12', 1, 540, 0.53, 2.10, 0.01
                )
            """), {
                "lote_id": ids.lote_id,
                "parametro_set_id": ids.parametro_set_id,
            })
            conexao_pg.execute(text(
                "SET CONSTRAINTS trg_fechamento_snapshot IMMEDIATE"
            ))
