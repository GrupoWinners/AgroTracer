import os
import uuid

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError

from app.domain.estados_lote import (
    EstadoLote,
    TransicaoLoteInvalida,
    validar_transicao_lote,
)


@pytest.mark.parametrize(
    "atual, novo",
    [
        (EstadoLote.RASCUNHO, EstadoLote.EM_MANEJO),
        (EstadoLote.EM_MANEJO, EstadoLote.FECHADO),
    ],
)
def test_transicoes_permitidas(atual, novo):
    validar_transicao_lote(atual, novo)


@pytest.mark.parametrize(
    "atual, novo",
    [
        (EstadoLote.RASCUNHO, EstadoLote.FECHADO),
        (EstadoLote.EM_MANEJO, EstadoLote.RASCUNHO),
        (EstadoLote.FECHADO, EstadoLote.EM_MANEJO),
        (EstadoLote.RASCUNHO, EstadoLote.RASCUNHO),
        (EstadoLote.FECHADO, EstadoLote.FECHADO),
    ],
)
def test_transicoes_proibidas(atual, novo):
    with pytest.raises(TransicaoLoteInvalida) as erro:
        validar_transicao_lote(atual, novo)

    assert erro.value.codigo == "LOTE_TRANSICAO_INVALIDA"


def test_status_invalido_postgresql():
    url = os.getenv("AGROTRACER_TEST_DATABASE_URL")

    if not url:
        pytest.skip("Banco de teste S2-T01 nao configurado")

    config = make_url(url)

    if (
        config.database != "agrotracer_s2_t01_teste"
        or config.host not in ("localhost", "127.0.0.1")
        or config.port != 55432
    ):
        pytest.fail("Use apenas o banco local S2-T01")

    engine = create_engine(url)

    try:
        with engine.connect() as conn:
            transacao = conn.begin()

            try:
                banco = conn.execute(
                    text("SELECT current_database()")
                ).scalar_one()

                assert banco == "agrotracer_s2_t01_teste"

                produtor_id = conn.execute(
                    text("""
                        INSERT INTO produtores (wordpress_user_id)
                        VALUES (:wp_id)
                        RETURNING id
                    """),
                    {
                        "wp_id": uuid.uuid4().int % 1000000000000 + 1,
                    },
                ).scalar_one()

                fazenda_id = conn.execute(
                    text("""
                        INSERT INTO fazendas (
                            produtor_id, nome, municipio, uf
                        )
                        VALUES (
                            :produtor_id, 'Fazenda RN04',
                            'Araguari', 'MG'
                        )
                        RETURNING id
                    """),
                    {"produtor_id": produtor_id},
                ).scalar_one()

                with pytest.raises(IntegrityError) as erro:
                    with conn.begin_nested():
                        conn.execute(
                            text("""
                                INSERT INTO lotes (
                                    fazenda_id, codigo_lote, status
                                )
                                VALUES (
                                    :fazenda_id, :codigo, 'INVALIDO'
                                )
                            """),
                            {
                                "fazenda_id": fazenda_id,
                                "codigo": f"RN04-{uuid.uuid4().hex[:12]}",
                            },
                        )

                assert erro.value.orig.sqlstate == "23514"

            finally:
                transacao.rollback()

    finally:
        engine.dispose()
