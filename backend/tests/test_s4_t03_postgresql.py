"""S4-T03: provas reais de integridade PostgreSQL com rollback."""

import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError

from test_s3_t01_db import cenario_pg  # noqa: F401


@pytest.fixture
def conexao_pg():
    url = os.getenv("AGROTRACER_TEST_DATABASE_URL")
    if not url:
        pytest.skip("PostgreSQL de teste nao configurado")
    if make_url(url).database != "agrotracer_s2_t01_teste":
        pytest.fail("Banco descartavel de teste obrigatorio")
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


def _inserir_fechamento(conn, ids):
    return conn.scalar(text("""
        INSERT INTO fechamentos_lote (
            lote_id, parametro_set_id, versao_metodo,
            data_abate, numero_animais_abate,
            peso_medio_abate_kg, rendimento_carcaca,
            emissao_total_kg_co2e, intensidade_kg_co2e_kg
        ) VALUES (
            :lote_id, :parametro_set_id, 'TESTE',
            '2026-11-12', 1, 540, 0.53, 2.10, 0.01
        ) RETURNING id
    """), {"lote_id": ids[0], "parametro_set_id": ids[1]})


def test_fechamento_sem_snapshot_nao_confirma(request):
    engine, ids = request.getfixturevalue("cenario_pg")
    with engine.connect() as conn:
        transacao = conn.begin()
        try:
            with pytest.raises(DBAPIError):
                with conn.begin_nested():
                    _inserir_fechamento(conn, ids)
                    conn.execute(text(
                        "SET CONSTRAINTS trg_fechamento_snapshot IMMEDIATE"
                    ))
        finally:
            transacao.rollback()


def test_snapshot_e_fechamento_nao_podem_ser_alterados(request):
    engine, ids = request.getfixturevalue("cenario_pg")
    with engine.connect() as conn:
        transacao = conn.begin()
        try:
            fechamento_id = _inserir_fechamento(conn, ids)
            snapshot_id = conn.scalar(text("""
                INSERT INTO snapshots_fechamento (
                    fechamento_id, lote_id, parametro_set_id,
                    versao_parametros, versao_metodo,
                    entradas, resultados
                ) VALUES (
                    :fechamento_id, :lote_id, :parametro_set_id,
                    'TESTE', 'TESTE', '{}'::jsonb, '{}'::jsonb
                ) RETURNING id
            """), {
                "fechamento_id": fechamento_id,
                "lote_id": ids[0],
                "parametro_set_id": ids[1],
            })
            for tabela, ident in (
                ("snapshots_fechamento", snapshot_id),
                ("fechamentos_lote", fechamento_id),
            ):
                with pytest.raises(DBAPIError):
                    with conn.begin_nested():
                        conn.execute(text(
                            f"UPDATE {tabela} SET id = id WHERE id = :id"
                        ), {"id": ident})
                with pytest.raises(DBAPIError):
                    with conn.begin_nested():
                        conn.execute(text(
                            f"DELETE FROM {tabela} WHERE id = :id"
                        ), {"id": ident})
        finally:
            transacao.rollback()
