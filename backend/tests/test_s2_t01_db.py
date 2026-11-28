import os
import uuid

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import configure_mappers

from app.models import Animal, Base, Lote, LoteAnimal
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier


def test_estrutura_modelos_s2_t01():
    """Valida a estrutura declarada dos modelos da Sprint 2."""
    configure_mappers()

    tabelas = Base.metadata.tables

    assert {"lotes", "animais", "lote_animais"}.issubset(tabelas)

    colunas_lotes = set(tabelas["lotes"].columns.keys())
    assert {
        "id",
        "fazenda_id",
        "codigo_lote",
        "status",
    }.issubset(colunas_lotes)

    colunas_animais = set(tabelas["animais"].columns.keys())
    assert {
        "id",
        "produtor_id",
        "identificador",
        "rfid",
        "data_nascimento_estimada",
    }.issubset(colunas_animais)

    # ADR-003: o lote atual nao fica armazenado em animais.
    assert "lote_id" not in colunas_animais

    colunas_associacoes = set(
        tabelas["lote_animais"].columns.keys()
    )
    assert {
        "id",
        "animal_id",
        "lote_id",
        "associado_em",
        "desassociado_em",
    }.issubset(colunas_associacoes)

    # RN-06: unicidade apenas das associacoes ativas.
    indice = next(
        indice
        for indice in LoteAnimal.__table__.indexes
        if indice.name == "uq_animal_associacao_ativa"
    )

    assert indice.unique
    assert list(indice.columns.keys()) == ["animal_id"]
    assert str(
        indice.dialect_options["postgresql"]["where"]
    ) == "desassociado_em IS NULL"

    # Protecao das referencias historicas.
    for modelo, coluna in (
        (Lote, "fazenda_id"),
        (Animal, "produtor_id"),
        (LoteAnimal, "animal_id"),
        (LoteAnimal, "lote_id"),
    ):
        fk = next(
            iter(modelo.__table__.c[coluna].foreign_keys)
        )
        assert fk.ondelete == "RESTRICT"


def test_s2_t01_associacao_temporal_postgresql():
    """RN-06: impede duas associacoes ativas e preserva historico."""
    url = os.getenv("AGROTRACER_TEST_DATABASE_URL")

    if not url:
        pytest.skip("Banco de teste S2-T01 nao configurado")

    banco_url = make_url(url)
    if (
        banco_url.database != "agrotracer_s2_t01_teste"
        or banco_url.host not in ("127.0.0.1", "localhost")
        or banco_url.port != 55432
    ):
        pytest.fail("Use apenas o PostgreSQL local de teste S2-T01")

    engine = create_engine(url)

    try:
        with engine.connect() as conn:
            transacao = conn.begin()

            try:
                banco = conn.execute(
                    text("SELECT current_database()")
                ).scalar_one()

                assert banco == "agrotracer_s2_t01_teste"

                wp_id = uuid.uuid4().int % 1000000000000 + 1

                produtor_id = conn.execute(
                    text("""
                        INSERT INTO produtores (wordpress_user_id)
                        VALUES (:wp_id)
                        RETURNING id
                    """),
                    {"wp_id": wp_id},
                ).scalar_one()

                fazenda_id = conn.execute(
                    text("""
                        INSERT INTO fazendas (
                            produtor_id, nome, municipio, uf
                        )
                        VALUES (
                            :produtor_id, 'Fazenda Teste S2',
                            'Araguari', 'MG'
                        )
                        RETURNING id
                    """),
                    {"produtor_id": produtor_id},
                ).scalar_one()

                lotes = []
                for _ in range(2):
                    codigo = f"S2-{uuid.uuid4().hex[:16]}"

                    lote_id = conn.execute(
                        text("""
                            INSERT INTO lotes (
                                fazenda_id, codigo_lote, status
                            )
                            VALUES (:fazenda_id, :codigo, 'EM_MANEJO')
                            RETURNING id
                        """),
                        {
                            "fazenda_id": fazenda_id,
                            "codigo": codigo,
                        },
                    ).scalar_one()

                    lotes.append(lote_id)

                identificador = f"S2-{uuid.uuid4().hex}"

                animal_id = conn.execute(
                    text("""
                        INSERT INTO animais (
                            produtor_id, identificador
                        )
                        VALUES (:produtor_id, :identificador)
                        RETURNING id
                    """),
                    {
                        "produtor_id": produtor_id,
                        "identificador": identificador,
                    },
                ).scalar_one()

                associacao_id = conn.execute(
                    text("""
                        INSERT INTO lote_animais (
                            animal_id, lote_id, associado_em
                        )
                        VALUES (
                            :animal_id, :lote_id,
                            '2026-10-20 12:00:00+00'
                        )
                        RETURNING id
                    """),
                    {
                        "animal_id": animal_id,
                        "lote_id": lotes[0],
                    },
                ).scalar_one()

                # RN-06: segunda associacao ativa deve falhar.
                with pytest.raises(IntegrityError) as erro:
                    with conn.begin_nested():
                        conn.execute(
                            text("""
                                INSERT INTO lote_animais (
                                    animal_id, lote_id
                                )
                                VALUES (:animal_id, :lote_id)
                            """),
                            {
                                "animal_id": animal_id,
                                "lote_id": lotes[1],
                            },
                        )

                assert erro.value.orig.sqlstate == "23505"

                # Encerra o primeiro vinculo sem apagar historico.
                conn.execute(
                    text("""
                        UPDATE lote_animais
                        SET desassociado_em =
                            '2026-10-21 12:00:00+00'
                        WHERE id = :id
                    """),
                    {"id": associacao_id},
                )

                # Nova associacao deve ser permitida.
                conn.execute(
                    text("""
                        INSERT INTO lote_animais (
                            animal_id, lote_id, associado_em
                        )
                        VALUES (
                            :animal_id, :lote_id,
                            '2026-10-22 12:00:00+00'
                        )
                    """),
                    {
                        "animal_id": animal_id,
                        "lote_id": lotes[1],
                    },
                )

                total, ativas = conn.execute(
                    text("""
                        SELECT
                            COUNT(*),
                            COUNT(*) FILTER (
                                WHERE desassociado_em IS NULL
                            )
                        FROM lote_animais
                        WHERE animal_id = :animal_id
                    """),
                    {"animal_id": animal_id},
                ).one()

                assert total == 2
                assert ativas == 1

            finally:
                transacao.rollback()

    finally:
        engine.dispose()


def test_s2_t01_constraints_postgresql():
    """Valida unicidade, periodo temporal e protecao historica."""
    url = os.getenv("AGROTRACER_TEST_DATABASE_URL")

    if not url:
        pytest.skip("Banco PostgreSQL S2-T01 nao configurado")

    banco_url = make_url(url)

    if (
        banco_url.database != "agrotracer_s2_t01_teste"
        or banco_url.host not in ("127.0.0.1", "localhost")
        or banco_url.port != 55432
    ):
        pytest.fail("Use somente o banco local de teste S2-T01")

    engine = create_engine(url)

    def verificar_erro(conn, sql, parametros, codigo):
        with pytest.raises(IntegrityError) as erro:
            with conn.begin_nested():
                conn.execute(text(sql), parametros)

        assert erro.value.orig.sqlstate == codigo

    try:
        with engine.connect() as conn:
            transacao = conn.begin()

            try:
                banco = conn.execute(
                    text("SELECT current_database()")
                ).scalar_one()

                assert banco == "agrotracer_s2_t01_teste"

                wp_id = uuid.uuid4().int % 1000000000000 + 1

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
                            produtor_id, nome, municipio, uf
                        )
                        VALUES (
                            :produtor, 'Fazenda S2',
                            'Araguari', 'MG'
                        )
                        RETURNING id
                    """),
                    {"produtor": produtor_id},
                ).scalar_one()

                lote_id = conn.execute(
                    text("""
                        INSERT INTO lotes (
                            fazenda_id, codigo_lote, status
                        )
                        VALUES (:fazenda, :codigo, 'RASCUNHO')
                        RETURNING id
                    """),
                    {
                        "fazenda": fazenda_id,
                        "codigo": f"S2-{uuid.uuid4().hex[:12]}",
                    },
                ).scalar_one()

                identificador = f"AN-{uuid.uuid4().hex}"

                animal_id = conn.execute(
                    text("""
                        INSERT INTO animais (
                            produtor_id, identificador
                        )
                        VALUES (:produtor, :identificador)
                        RETURNING id
                    """),
                    {
                        "produtor": produtor_id,
                        "identificador": identificador,
                    },
                ).scalar_one()

                # RN-05: identificador unico.
                verificar_erro(
                    conn,
                    """
                    INSERT INTO animais (
                        produtor_id, identificador
                    )
                    VALUES (:produtor, :identificador)
                    """,
                    {
                        "produtor": produtor_id,
                        "identificador": identificador,
                    },
                    "23505",
                )

                # Cria associacao historica valida.
                conn.execute(
                    text("""
                        INSERT INTO lote_animais (
                            animal_id, lote_id,
                            associado_em, desassociado_em
                        )
                        VALUES (
                            :animal, :lote,
                            '2026-10-20 12:00:00+00',
                            '2026-10-21 12:00:00+00'
                        )
                    """),
                    {"animal": animal_id, "lote": lote_id},
                )

                # Periodo com fim anterior ao inicio.
                verificar_erro(
                    conn,
                    """
                    INSERT INTO lote_animais (
                        animal_id, lote_id,
                        associado_em, desassociado_em
                    )
                    VALUES (
                        :animal, :lote,
                        '2026-10-22 12:00:00+00',
                        '2026-10-21 12:00:00+00'
                    )
                    """,
                    {"animal": animal_id, "lote": lote_id},
                    "23514",
                )

                # Nao permite apagar lote historico.
                verificar_erro(
                    conn,
                    "DELETE FROM lotes WHERE id = :id",
                    {"id": lote_id},
                    "23503",
                )

                # Nao permite apagar animal historico.
                verificar_erro(
                    conn,
                    "DELETE FROM animais WHERE id = :id",
                    {"id": animal_id},
                    "23503",
                )

                print("RN-05: identificador unico OK")
                print("Integridade temporal: OK")
                print("ON DELETE RESTRICT: OK")

            finally:
                transacao.rollback()

    finally:
        engine.dispose()


def test_s2_t01_concorrencia_associacao_ativa():
    """RN-06: duas transacoes nao criam vinculos ativos duplicados."""
    url = os.getenv("AGROTRACER_TEST_DATABASE_URL")

    if not url:
        pytest.skip("Banco PostgreSQL S2-T01 nao configurado")

    config = make_url(url)
    if (
        config.database != "agrotracer_s2_t01_teste"
        or config.host not in ("127.0.0.1", "localhost")
        or config.port != 55432
    ):
        pytest.fail("Use apenas o banco local de teste S2-T01")

    engine = create_engine(url)
    animal_id = None

    try:
        with engine.begin() as conn:
            assert conn.execute(
                text("SELECT current_database()")
            ).scalar_one() == "agrotracer_s2_t01_teste"

            produtor_id = conn.execute(
                text("""
                    INSERT INTO produtores (wordpress_user_id)
                    VALUES (:wp)
                    RETURNING id
                """),
                {"wp": uuid.uuid4().int % 1000000000000 + 1},
            ).scalar_one()

            fazenda_id = conn.execute(
                text("""
                    INSERT INTO fazendas (
                        produtor_id, nome, municipio, uf
                    )
                    VALUES (:p, 'Fazenda Concorrencia', 'Araguari', 'MG')
                    RETURNING id
                """),
                {"p": produtor_id},
            ).scalar_one()

            lotes = []

            for _ in range(2):
                lote_id = conn.execute(
                    text("""
                        INSERT INTO lotes (
                            fazenda_id, codigo_lote, status
                        )
                        VALUES (:f, :codigo, 'RASCUNHO')
                        RETURNING id
                    """),
                    {
                        "f": fazenda_id,
                        "codigo": f"S2-{uuid.uuid4().hex[:20]}",
                    },
                ).scalar_one()

                lotes.append(lote_id)

            animal_id = conn.execute(
                text("""
                    INSERT INTO animais (
                        produtor_id, identificador
                    )
                    VALUES (:p, :identificador)
                    RETURNING id
                """),
                {
                    "p": produtor_id,
                    "identificador": f"AN-{uuid.uuid4().hex}",
                },
            ).scalar_one()

        barreira = Barrier(2)

        def tentar_associar(lote_id):
            try:
                with engine.begin() as conn:
                    conn.execute(
                        text("SET LOCAL lock_timeout = '10s'")
                    )

                    # As duas transacoes chegam juntas ao INSERT.
                    barreira.wait(timeout=5)

                    conn.execute(
                        text("""
                            INSERT INTO lote_animais (
                                animal_id, lote_id
                            )
                            VALUES (:animal, :lote)
                        """),
                        {"animal": animal_id, "lote": lote_id},
                    )

                return "ACEITO"

            except IntegrityError as erro:
                assert erro.orig.sqlstate == "23505"
                assert (
                    erro.orig.diag.constraint_name
                    == "uq_animal_associacao_ativa"
                )
                return "BLOQUEADO"

        with ThreadPoolExecutor(max_workers=2) as executor:
            futuros = [
                executor.submit(tentar_associar, lote_id)
                for lote_id in lotes
            ]
            resultados = [f.result() for f in futuros]

        assert sorted(resultados) == ["ACEITO", "BLOQUEADO"]

        with engine.connect() as conn:
            ativas = conn.execute(
                text("""
                    SELECT COUNT(*)
                    FROM lote_animais
                    WHERE animal_id = :animal
                      AND desassociado_em IS NULL
                """),
                {"animal": animal_id},
            ).scalar_one()

        assert ativas == 1

    finally:
        try:
            if animal_id is not None:
                with engine.begin() as conn:
                    conn.execute(
                        text("""
                            DELETE FROM lote_animais
                            WHERE animal_id = :animal
                        """),
                        {"animal": animal_id},
                    )
                    conn.execute(
                        text("DELETE FROM animais WHERE id = :id"),
                        {"id": animal_id},
                    )
                    for lote_id in lotes:
                        conn.execute(
                            text("DELETE FROM lotes WHERE id = :id"),
                            {"id": lote_id},
                        )
                    conn.execute(
                        text("DELETE FROM fazendas WHERE id = :id"),
                        {"id": fazenda_id},
                    )
                    conn.execute(
                        text("DELETE FROM produtores WHERE id = :id"),
                        {"id": produtor_id},
                    )
        finally:
            engine.dispose()
