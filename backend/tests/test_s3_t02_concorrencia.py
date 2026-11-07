"""S3-T02: concorrencia real na ativacao de parametros."""

import os
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from uuid import uuid4

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.services.parametro_service import ativar_parametro_set


def test_ativacoes_concorrentes_sao_serializadas():
    url = os.environ["AGROTRACER_TEST_DATABASE_URL"]

    assert make_url(url).database == "agrotracer_s2_t01_teste"

    engine = create_engine(url)
    ids = []
    primeira_ativa = Event()
    liberar_primeira = Event()

    try:
        # Cria dois conjuntos de teste inicialmente
        # em RASCUNHO, com um fator sintetico cada.
        with engine.begin() as conn:
            for _ in range(2):
                conjunto_id = conn.scalar(
                    text("""
                        INSERT INTO parametro_sets
                            (versao, status, vigencia_inicio)
                        VALUES
                            (:versao, 'RASCUNHO', '2026-01-01')
                        RETURNING id
                    """),
                    {"versao": f"CONCORRENCIA-{uuid4().hex}"},
                )

                ids.append(conjunto_id)

                conn.execute(
                    text("""
                        INSERT INTO fatores
                            (parametro_set_id, chave,
                             unidade, valor, source_type)
                        VALUES
                            (:id, 'FATOR_TESTE',
                             'kg CO2e/cabeca/dia',
                             2.10, 'SYNTHETIC')
                    """),
                    {"id": conjunto_id},
                )

        def primeira_ativacao():
            with Session(engine) as db:
                try:
                    ativar_parametro_set(
                        db=db,
                        parametro_set_id=ids[0],
                        wordpress_user_id=42,
                        justificativa="Teste concorrente A",
                    )

                    # Mantem lock sem confirmar a transacao.
                    primeira_ativa.set()

                    assert liberar_primeira.wait(10), (
                        "Tempo esgotado aguardando "
                        "liberacao da primeira transacao."
                    )
                finally:
                    db.rollback()

        def segunda_ativacao():
            assert primeira_ativa.wait(10), (
                "Primeira ativacao nao iniciou."
            )

            with Session(engine) as db:
                try:
                    # Se o lock funcionar, esta transacao
                    # deve atingir o limite de espera.
                    db.execute(
                        text(
                            "SET LOCAL lock_timeout = '800ms'"
                        )
                    )

                    ativar_parametro_set(
                        db=db,
                        parametro_set_id=ids[1],
                        wordpress_user_id=42,
                        justificativa="Teste concorrente B",
                    )

                except DBAPIError as erro:
                    assert erro.orig.sqlstate == "55P03", (
                        "Esperado bloqueio transacional "
                        "do PostgreSQL."
                    )

                else:
                    raise AssertionError(
                        "A segunda ativacao nao aguardou "
                        "o lock da primeira."
                    )

                finally:
                    db.rollback()

        with ThreadPoolExecutor(max_workers=2) as executor:
            primeira = executor.submit(primeira_ativacao)
            segunda = executor.submit(segunda_ativacao)

            try:
                segunda.result(timeout=15)
            finally:
                liberar_primeira.set()

            primeira.result(timeout=15)

        # Ambas as transacoes foram desfeitas.
        # Nenhuma versao de teste fica publicada.
        with engine.connect() as conn:
            for conjunto_id in ids:
                status = conn.scalar(
                    text("""
                        SELECT status
                        FROM parametro_sets
                        WHERE id = :id
                    """),
                    {"id": conjunto_id},
                )
                assert status == "RASCUNHO"

    finally:
        liberar_primeira.set()

        # Limpeza dos registros temporarios.
        with engine.begin() as conn:
            for conjunto_id in ids:
                conn.execute(
                    text("""
                        DELETE FROM fatores
                        WHERE parametro_set_id = :id
                    """),
                    {"id": conjunto_id},
                )

                conn.execute(
                    text("""
                        DELETE FROM parametro_sets
                        WHERE id = :id
                    """),
                    {"id": conjunto_id},
                )

        engine.dispose()
