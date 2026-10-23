import os
import uuid

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError


def test_s1_t01_postgresql():
    url = os.getenv("AGROTRACER_TEST_DATABASE_URL")

    if not url:
        pytest.skip("Banco de teste S1-T01 nao configurado")

    if make_url(url).database != "agrotracer_s1_t01_teste":
        pytest.fail("Use apenas o banco descartavel da S1-T01")

    engine = create_engine(url)

    try:
        tabelas = set(inspect(engine).get_table_names())

        assert {
            "produtores",
            "fazendas",
            "talhoes",
            "auditoria_eventos",
        }.issubset(tabelas)

        with engine.connect() as conn:
            resultado = conn.execute(text("""
                SELECT conname, confdeltype
                FROM pg_constraint
                WHERE conname IN (
                    'fk_fazendas_produtor_id',
                    'fk_talhoes_fazenda_id'
                )
            """))
            fks = dict(resultado.fetchall())

        assert fks == {
            "fk_fazendas_produtor_id": "r",
            "fk_talhoes_fazenda_id": "r",
        }

        wp_id = uuid.uuid4().int % 1000000000000 + 1

        with engine.begin() as conn:
            produtor_id = conn.execute(
                text("""
                    INSERT INTO produtores (wordpress_user_id)
                    VALUES (:wp)
                    RETURNING id
                """),
                {"wp": wp_id},
            ).scalar_one()

            fazenda_id = conn.execute(
                text("""
                    INSERT INTO fazendas (
                        produtor_id, numero_car_informado
                    )
                    VALUES (:produtor, :car)
                    RETURNING id
                """),
                {
                    "produtor": produtor_id,
                    "car": "CAR DECLARADO PARA TESTE",
                },
            ).scalar_one()

            talhao_id = conn.execute(
                text("""
                    INSERT INTO talhoes (
                        fazenda_id, area_hectares
                    )
                    VALUES (:fazenda, 2.5000)
                    RETURNING id
                """),
                {"fazenda": fazenda_id},
            ).scalar_one()

            auditoria_id = conn.execute(
                text("""
                    INSERT INTO auditoria_eventos (
                        entidade, entidade_id, acao,
                        wordpress_user_id, correlation_id
                    )
                    VALUES (
                        'fazendas', :fazenda, 'CRIAR',
                        :wp, 'teste-s1-t01'
                    )
                    RETURNING id
                """),
                {"fazenda": fazenda_id, "wp": wp_id},
            ).scalar_one()

        assert all([
            produtor_id, fazenda_id, talhao_id, auditoria_id,
        ])

        def deve_rejeitar(sql, parametros, codigo):
            with pytest.raises(IntegrityError) as erro:
                with engine.begin() as conn:
                    conn.execute(text(sql), parametros)

            assert erro.value.orig.sqlstate == codigo

        deve_rejeitar(
            "INSERT INTO produtores (wordpress_user_id) "
            "VALUES (:wp)",
            {"wp": wp_id},
            "23505",
        )

        deve_rejeitar(
            "INSERT INTO produtores (wordpress_user_id) "
            "VALUES (0)",
            {},
            "23514",
        )

        deve_rejeitar(
            "INSERT INTO talhoes "
            "(fazenda_id, area_hectares) "
            "VALUES (:fazenda, 0)",
            {"fazenda": fazenda_id},
            "23514",
        )

        deve_rejeitar(
            "INSERT INTO talhoes "
            "(fazenda_id, area_hectares) "
            "VALUES (:fazenda, -1)",
            {"fazenda": fazenda_id},
            "23514",
        )

        deve_rejeitar(
            "INSERT INTO fazendas (produtor_id) "
            "VALUES (-999999)",
            {},
            "23503",
        )

        deve_rejeitar(
            "INSERT INTO talhoes "
            "(fazenda_id, area_hectares) "
            "VALUES (-999999, 1)",
            {},
            "23503",
        )

        deve_rejeitar(
            "DELETE FROM fazendas WHERE id = :id",
            {"id": fazenda_id},
            "23503",
        )

        deve_rejeitar(
            "DELETE FROM produtores WHERE id = :id",
            {"id": produtor_id},
            "23503",
        )

        deve_rejeitar(
            "INSERT INTO auditoria_eventos "
            "(entidade, acao) VALUES ('fazendas', '')",
            {},
            "23514",
        )

    finally:
        engine.dispose()
