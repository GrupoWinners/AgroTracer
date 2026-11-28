import os
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError


@pytest.fixture
def db_pg():
    url = os.environ.get("AGROTRACER_TEST_DATABASE_URL")
    assert url, "Configure o PostgreSQL de testes."
    assert make_url(url).database == "agrotracer_s2_t01_teste"

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


def criar_conjunto(conn):
    versao = f"S3-T02-{uuid4().hex}"

    conjunto_id = conn.scalar(
        text("""
            INSERT INTO parametro_sets
                (versao, status, vigencia_inicio)
            VALUES (:versao, 'RASCUNHO', '2026-01-01')
            RETURNING id
        """),
        {"versao": versao},
    )

    return conjunto_id, versao


def criar_fator(
    conn,
    conjunto_id,
    source_type="SYNTHETIC",
    source_uri=None,
    unidade="kg CO2e/cabeca/dia",
):
    return conn.scalar(
        text("""
            INSERT INTO fatores
                (parametro_set_id, chave, unidade,
                 valor, source_type, source_uri)
            VALUES
                (:conjunto, :chave, :unidade,
                 :valor, :source_type, :source_uri)
            RETURNING id
        """),
        {
            "conjunto": conjunto_id,
            "chave": f"FE-{uuid4().hex}",
            "unidade": unidade,
            "valor": Decimal("2.100000000000"),
            "source_type": source_type,
            "source_uri": source_uri,
        },
    )


def deve_falhar(conn, comando, parametros, codigo):
    with pytest.raises(DBAPIError) as erro:
        with conn.begin_nested():
            conn.execute(text(comando), parametros)

    assert erro.value.orig.sqlstate == codigo


def ativar(conn, conjunto_id):
    conn.execute(
        text("""
            UPDATE parametro_sets
            SET status = 'ATIVO',
                aprovado_por = 'QA-TESTE',
                aprovado_em = now()
            WHERE id = :id
        """),
        {"id": conjunto_id},
    )


def test_fator_sintetico_usa_decimal(db_pg):
    conjunto_id, _ = criar_conjunto(db_pg)
    fator_id = criar_fator(db_pg, conjunto_id)

    valor = db_pg.scalar(
        text("SELECT valor FROM fatores WHERE id = :id"),
        {"id": fator_id},
    )

    assert isinstance(valor, Decimal)
    assert valor == Decimal("2.100000000000")


@pytest.mark.parametrize(
    "source_type,source_uri,unidade",
    [
        ("INVALIDO", None, "kg"),
        ("IPCC", None, "kg"),
        ("SYNTHETIC", None, ""),
    ],
)
def test_rejeitar_fonte_ou_unidade_invalida(
    db_pg, source_type, source_uri, unidade
):
    conjunto_id, _ = criar_conjunto(db_pg)

    comando = """
        INSERT INTO fatores
            (parametro_set_id, chave, unidade,
             valor, source_type, source_uri)
        VALUES
            (:conjunto, :chave, :unidade,
             2.10, :fonte, :uri)
    """

    deve_falhar(
        db_pg,
        comando,
        {
            "conjunto": conjunto_id,
            "chave": uuid4().hex,
            "unidade": unidade,
            "fonte": source_type,
            "uri": source_uri,
        },
        "23514",
    )


def test_versao_ativa_unica(db_pg):
    conjunto_a, versao_a = criar_conjunto(db_pg)
    conjunto_b, _ = criar_conjunto(db_pg)

    ativar(db_pg, conjunto_a)

    deve_falhar(
        db_pg,
        """
        UPDATE parametro_sets
        SET status = 'ATIVO',
            aprovado_por = 'QA-TESTE',
            aprovado_em = now()
        WHERE id = :id
        """,
        {"id": conjunto_b},
        "23505",
    )

    deve_falhar(
        db_pg,
        """
        INSERT INTO parametro_sets
            (versao, status, vigencia_inicio)
        VALUES (:versao, 'RASCUNHO', '2026-01-01')
        """,
        {"versao": versao_a},
        "23505",
    )


def test_ativacao_exige_aprovacao(db_pg):
    conjunto_id, _ = criar_conjunto(db_pg)

    deve_falhar(
        db_pg,
        """
        UPDATE parametro_sets
        SET status = 'ATIVO'
        WHERE id = :id
        """,
        {"id": conjunto_id},
        "23514",
    )


def test_historico_publicado_imutavel(db_pg):
    conjunto_id, _ = criar_conjunto(db_pg)
    fator_id = criar_fator(db_pg, conjunto_id)

    ativar(db_pg, conjunto_id)

    # Não pode alterar um fator publicado.
    deve_falhar(
        db_pg,
        "UPDATE fatores SET valor = 9 WHERE id = :id",
        {"id": fator_id},
        "P0001",
    )

    # Não pode apagar o fator publicado.
    deve_falhar(
        db_pg,
        "DELETE FROM fatores WHERE id = :id",
        {"id": fator_id},
        "P0001",
    )

    # Não pode modificar o conteúdo do conjunto.
    deve_falhar(
        db_pg,
        """
        UPDATE parametro_sets
        SET versao = 'ALTERADA'
        WHERE id = :id
        """,
        {"id": conjunto_id},
        "P0001",
    )

    # Não pode excluir versão publicada.
    deve_falhar(
        db_pg,
        "DELETE FROM parametro_sets WHERE id = :id",
        {"id": conjunto_id},
        "P0001",
    )

    # Pode tornar inativa a versão publicada.
    db_pg.execute(
        text("""
            UPDATE parametro_sets
            SET status = 'INATIVO'
            WHERE id = :id
        """),
        {"id": conjunto_id},
    )

    # Mesmo inativa, continua protegida.
    deve_falhar(
        db_pg,
        "UPDATE fatores SET valor = 5 WHERE id = :id",
        {"id": fator_id},
        "P0001",
    )
