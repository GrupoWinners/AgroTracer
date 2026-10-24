import os
import uuid

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError

from app.models import Base


def test_modelos_metadata_estrutura():
    """Valida a definicao declarativa das tabelas e colunas (executa no CI)."""
    tabelas = Base.metadata.tables

    assert "produtores" in tabelas
    assert "fazendas" in tabelas
    assert "talhoes" in tabelas
    assert "auditoria_eventos" in tabelas

    # Produtores
    colunas_produtores = set(tabelas["produtores"].columns.keys())
    assert {"id", "wordpress_user_id"}.issubset(colunas_produtores)

    # Fazendas
    colunas_fazendas = set(tabelas["fazendas"].columns.keys())
    assert {
        "id",
        "produtor_id",
        "nome",
        "municipio",
        "uf",
        "numero_car_informado",
    }.issubset(colunas_fazendas)

    # Talhoes
    colunas_talhoes = set(tabelas["talhoes"].columns.keys())
    assert {
        "id",
        "fazenda_id",
        "identificador",
        "area_hectares",
    }.issubset(colunas_talhoes)

    # Auditoria
    colunas_auditoria = set(tabelas["auditoria_eventos"].columns.keys())
    assert {
        "id",
        "entidade",
        "entidade_id",
        "acao",
        "wordpress_user_id",
        "correlation_id",
        "detalhes",
        "criado_em",
    }.issubset(colunas_auditoria)


def test_s1_t01_postgresql():
    """Valida constraints e integridade no PostgreSQL quando configurado."""
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
        car_unico = f"MS-{uuid.uuid4().hex[:8].upper()}"

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
                        produtor_id, nome, municipio, uf, numero_car_informado
                    )
                    VALUES (:produtor, :nome, :municipio, :uf, :car)
                    RETURNING id
                """),
                {
                    "produtor": produtor_id,
                    "nome": "Fazenda Modelo",
                    "municipio": "Aquidauana",
                    "uf": "MS",
                    "car": car_unico,
                },
            ).scalar_one()

            talhao_id = conn.execute(
                text("""
                    INSERT INTO talhoes (
                        fazenda_id, identificador, area_hectares
                    )
                    VALUES (:fazenda, :identificador, 2.5000)
                    RETURNING id
                """),
                {
                    "fazenda": fazenda_id,
                    "identificador": "Piquete 01",
                },
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

        # Produtor duplicado
        deve_rejeitar(
            "INSERT INTO produtores (wordpress_user_id) VALUES (:wp)",
            {"wp": wp_id},
            "23505",
        )

        # Produtor com ID invalido
        deve_rejeitar(
            "INSERT INTO produtores (wordpress_user_id) VALUES (0)",
            {},
            "23514",
        )

        # Fazenda com nome vazio
        deve_rejeitar(
            "INSERT INTO fazendas (produtor_id, nome, municipio, uf) "
            "VALUES (:produtor, '   ', 'Aquidauana', 'MS')",
            {"produtor": produtor_id},
            "23514",
        )

        # Fazenda com UF invalida
        deve_rejeitar(
            "INSERT INTO fazendas (produtor_id, nome, municipio, uf) "
            "VALUES (:produtor, 'Fazenda Teste', 'Aquidauana', 'MSX')",
            {"produtor": produtor_id},
            "23514",
        )

        # Duplicidade de CAR (RN-02)
        deve_rejeitar(
            "INSERT INTO fazendas "
            "(produtor_id, nome, municipio, uf, numero_car_informado) "
            "VALUES (:produtor, 'Outra Fazenda', 'Campo Grande', 'MS', :car)",
            {"produtor": produtor_id, "car": car_unico},
            "23505",
        )

        # Talhao com area zero
        deve_rejeitar(
            "INSERT INTO talhoes (fazenda_id, identificador, area_hectares) "
            "VALUES (:fazenda, 'Piquete 02', 0)",
            {"fazenda": fazenda_id},
            "23514",
        )

        # Talhao com identificador vazio
        deve_rejeitar(
            "INSERT INTO talhoes (fazenda_id, identificador, area_hectares) "
            "VALUES (:fazenda, '  ', 10)",
            {"fazenda": fazenda_id},
            "23514",
        )

        # Talhao duplicado na mesma fazenda
        deve_rejeitar(
            "INSERT INTO talhoes (fazenda_id, identificador, area_hectares) "
            "VALUES (:fazenda, 'Piquete 01', 5.0)",
            {"fazenda": fazenda_id},
            "23505",
        )

        # FK invalida de produtor
        deve_rejeitar(
            "INSERT INTO fazendas (produtor_id, nome, municipio, uf) "
            "VALUES (-999999, 'Fazenda Sem Dono', 'Aquidauana', 'MS')",
            {},
            "23503",
        )

        # FK invalida de fazenda
        deve_rejeitar(
            "INSERT INTO talhoes (fazenda_id, identificador, area_hectares) "
            "VALUES (-999999, 'Piquete 99', 1)",
            {},
            "23503",
        )

        # ON DELETE RESTRICT em fazenda
        deve_rejeitar(
            "DELETE FROM fazendas WHERE id = :id",
            {"id": fazenda_id},
            "23503",
        )

        # ON DELETE RESTRICT em produtor
        deve_rejeitar(
            "DELETE FROM produtores WHERE id = :id",
            {"id": produtor_id},
            "23503",
        )

        # Auditoria acao vazia
        deve_rejeitar(
            "INSERT INTO auditoria_eventos "
            "(entidade, acao) VALUES ('fazendas', '')",
            {},
            "23514",
        )

    finally:
        engine.dispose()
