import os
import uuid

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DataError, IntegrityError


def test_s1_t01_postgresql():
    url = os.getenv("AGROTRACER_TEST_DATABASE_URL")

    if not url:
        pytest.skip("Banco de integracao S1-T01 nao configurado")

    if make_url(url).database != "agrotracer_s1_t01_migracao_teste":
        pytest.fail("Use apenas o banco isolado de migracao S1-T01")

    engine = create_engine(url)

    try:
        inspetor = inspect(engine)

        assert {
            "produtores",
            "fazendas",
            "talhoes",
            "auditoria_eventos",
        }.issubset(set(inspetor.get_table_names()))

        with engine.connect() as conn:
            fks = dict(conn.execute(text("""
                SELECT conname, confdeltype
                FROM pg_constraint
                WHERE conname IN (
                    'fk_fazendas_produtor_id',
                    'fk_talhoes_fazenda_id'
                )
            """)).fetchall())

        assert fks == {
            "fk_fazendas_produtor_id": "r",
            "fk_talhoes_fazenda_id": "r",
        }

        uniques = {
            item["name"]
            for item in inspetor.get_unique_constraints("fazendas")
        }
        assert "uq_fazendas_numero_car_informado" in uniques

        wp_id = uuid.uuid4().int % 1000000000000 + 1
        car = "CAR-TESTE-" + uuid.uuid4().hex

        with engine.connect() as conn:
            transacao = conn.begin()

            try:
                produtor_id = conn.execute(text("""
                    INSERT INTO produtores (wordpress_user_id)
                    VALUES (:wp)
                    RETURNING id
                """), {"wp": wp_id}).scalar_one()

                fazenda_id = conn.execute(text("""
                    INSERT INTO fazendas (
                        produtor_id, nome, municipio, uf,
                        numero_car_informado
                    )
                    VALUES (
                        :produtor, 'Fazenda Teste',
                        'Araguari', 'MG', :car
                    )
                    RETURNING id
                """), {
                    "produtor": produtor_id,
                    "car": car,
                }).scalar_one()

                talhao_id = conn.execute(text("""
                    INSERT INTO talhoes (
                        fazenda_id, identificador, area_hectares
                    )
                    VALUES (:fazenda, 'Piquete 01', 2.5000)
                    RETURNING id
                """), {"fazenda": fazenda_id}).scalar_one()

                auditoria_id = conn.execute(text("""
                    INSERT INTO auditoria_eventos (
                        entidade, entidade_id, acao,
                        wordpress_user_id, correlation_id
                    )
                    VALUES (
                        'fazendas', :fazenda, 'CRIAR',
                        :wp, 'teste-s1-t01'
                    )
                    RETURNING id
                """), {
                    "fazenda": fazenda_id,
                    "wp": wp_id,
                }).scalar_one()

                assert all((
                    produtor_id, fazenda_id,
                    talhao_id, auditoria_id,
                ))

                def rejeitar(
                    sql, parametros, codigo,
                    tipo_erro=IntegrityError
                ):
                    with pytest.raises(tipo_erro) as erro:
                        with conn.begin_nested():
                            conn.execute(text(sql), parametros)

                    assert erro.value.orig.sqlstate == codigo

                # Identidade WordPress unica.
                rejeitar(
                    "INSERT INTO produtores (wordpress_user_id) "
                    "VALUES (:wp)",
                    {"wp": wp_id},
                    "23505",
                )

                # Identidade de sistema nao e produtor.
                rejeitar(
                    "INSERT INTO produtores (wordpress_user_id) "
                    "VALUES (0)",
                    {},
                    "23514",
                )

                # RN-02: CAR nao nulo deve ser unico.
                rejeitar("""
                    INSERT INTO fazendas (
                        produtor_id, nome, municipio, uf,
                        numero_car_informado
                    )
                    VALUES (
                        :produtor, 'Outra Fazenda',
                        'Araguari', 'MG', :car
                    )
                """, {
                    "produtor": produtor_id,
                    "car": car,
                }, "23505")

                # CAR nulo e permitido em varias fazendas.
                for nome in ("Sem CAR 1", "Sem CAR 2"):
                    conn.execute(text("""
                        INSERT INTO fazendas (
                            produtor_id, nome, municipio, uf
                        )
                        VALUES (
                            :produtor, :nome, 'Araguari', 'MG'
                        )
                    """), {
                        "produtor": produtor_id,
                        "nome": nome,
                    })

                # Campos cadastrais obrigatorios.
                for campo in ("nome", "municipio", "uf"):
                    valores = {
                        "produtor": produtor_id,
                        "nome": "Fazenda",
                        "municipio": "Araguari",
                        "uf": "MG",
                    }

                    valores[campo] = None

                    rejeitar(
                        """
                        INSERT INTO fazendas (
                            produtor_id, nome, municipio, uf
                        )
                        VALUES (
                            :produtor, :nome, :municipio, :uf
                        )
                        """,
                        valores,
                        "23502",
                    )

                # UF acima de VARCHAR(2): SQLSTATE 22001.
                rejeitar("""
                    INSERT INTO fazendas (
                        produtor_id, nome, municipio, uf
                    )
                    VALUES (
                        :produtor, 'Fazenda', 'Araguari', 'MSX'
                    )
                """, {"produtor": produtor_id}, "22001", DataError)

                # Identificador de talhao obrigatorio.
                rejeitar("""
                    INSERT INTO talhoes (
                        fazenda_id, area_hectares
                    )
                    VALUES (:fazenda, 1)
                """, {"fazenda": fazenda_id}, "23502")

                # RN-03: area maior que zero.
                for area in (0, -1):
                    rejeitar("""
                        INSERT INTO talhoes (
                            fazenda_id, identificador,
                            area_hectares
                        )
                        VALUES (:fazenda, 'Piquete', :area)
                    """, {
                        "fazenda": fazenda_id,
                        "area": area,
                    }, "23514")

                # FKs obrigatorias e validas.
                rejeitar("""
                    INSERT INTO fazendas (
                        produtor_id, nome, municipio, uf
                    )
                    VALUES (
                        -999999, 'Invalida', 'Araguari', 'MG'
                    )
                """, {}, "23503")

                rejeitar("""
                    INSERT INTO talhoes (
                        fazenda_id, identificador, area_hectares
                    )
                    VALUES (-999999, 'Invalido', 1)
                """, {}, "23503")

                # Exclusoes bloqueadas por RESTRICT.
                rejeitar(
                    "DELETE FROM fazendas WHERE id = :id",
                    {"id": fazenda_id},
                    "23503",
                )

                rejeitar(
                    "DELETE FROM produtores WHERE id = :id",
                    {"id": produtor_id},
                    "23503",
                )

                # Auditoria exige acao preenchida.
                rejeitar("""
                    INSERT INTO auditoria_eventos (
                        entidade, acao
                    )
                    VALUES ('fazendas', '')
                """, {}, "23514")

            finally:
                transacao.rollback()

    finally:
        engine.dispose()
