import os
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError


@pytest.fixture
def conexao_pg():
    url = os.environ.get("AGROTRACER_TEST_DATABASE_URL")

    if not url:
        pytest.skip("PostgreSQL de teste nao configurado.")

    assert make_url(url).database == "agrotracer_s2_t01_teste"

    engine = create_engine(url)

    try:
        with engine.connect() as conn:
            transacao = conn.begin()

            try:
                yield conn, engine
            finally:
                # Nenhum registro de teste permanece no banco.
                transacao.rollback()
    finally:
        engine.dispose()


def exigir_erro(conn, comando, parametros, codigo, constraint):
    with pytest.raises(IntegrityError) as capturado:
        with conn.begin_nested():
            conn.execute(text(comando), parametros)

    erro = capturado.value.orig

    assert erro.sqlstate == codigo
    assert erro.diag.constraint_name == constraint


def preparar_animal(conn):
    sufixo = uuid4().hex

    produtor_id = conn.scalar(
        text(
            "INSERT INTO produtores (wordpress_user_id) "
            "VALUES (:wp) RETURNING id"
        ),
        {"wp": uuid4().int % 9000000000 + 1},
    )

    animal_id = conn.scalar(
        text(
            "INSERT INTO animais (produtor_id, identificador) "
            "VALUES (:produtor, :identificador) RETURNING id"
        ),
        {
            "produtor": produtor_id,
            "identificador": f"TESTE-S2T03-{sufixo}",
        },
    )

    return animal_id


def test_constraints_e_fks_movimentacao(conexao_pg):
    conn, engine = conexao_pg

    tabelas = inspect(engine).get_table_names()
    assert "movimentacoes" in tabelas

    fks = inspect(engine).get_foreign_keys("movimentacoes")

    assert len(fks) == 4
    assert all(
        fk["options"].get("ondelete") == "RESTRICT"
        for fk in fks
    )

    animal_id = preparar_animal(conn)

    comando = """
        INSERT INTO movimentacoes
            (animal_id, lote_id, origem_talhao_id,
             destino_talhao_id, tipo, data_hora)
        VALUES
            (:animal, :lote, :origem, :destino,
             'TRANSFERENCIA', now())
    """

    # Nenhum alvo: proibido pelo CHECK XOR.
    exigir_erro(
        conn,
        comando,
        {
            "animal": None,
            "lote": None,
            "origem": None,
            "destino": None,
        },
        "23514",
        "ck_movimentacoes_alvo_xor",
    )

    # Dois alvos: proibido pelo CHECK XOR.
    exigir_erro(
        conn,
        comando,
        {
            "animal": animal_id,
            "lote": 999999999999,
            "origem": None,
            "destino": None,
        },
        "23514",
        "ck_movimentacoes_alvo_xor",
    )

    # Origem igual ao destino: proibido.
    exigir_erro(
        conn,
        comando,
        {
            "animal": animal_id,
            "lote": None,
            "origem": 999999999999,
            "destino": 999999999999,
        },
        "23514",
        "ck_movimentacoes_origem_destino",
    )

    # Chave estrangeira invalida: proibida.
    exigir_erro(
        conn,
        comando,
        {
            "animal": 999999999999,
            "lote": None,
            "origem": None,
            "destino": None,
        },
        "23503",
        "fk_movimentacoes_animal_id",
    )

    # Registro valido: deve funcionar.
    conn.execute(
        text(comando),
        {
            "animal": animal_id,
            "lote": None,
            "origem": None,
            "destino": None,
        },
    )

    quantidade = conn.scalar(
        text(
            "SELECT COUNT(*) FROM movimentacoes "
            "WHERE animal_id = :animal"
        ),
        {"animal": animal_id},
    )

    assert quantidade == 1

    # Referencia historica impede exclusao do animal.
    exigir_erro(
        conn,
        "DELETE FROM animais WHERE id = :animal",
        {"animal": animal_id},
        "23503",
        "fk_movimentacoes_animal_id",
    )
