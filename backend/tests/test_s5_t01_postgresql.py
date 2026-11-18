"""Indice parcial e idempotencia no PostgreSQL real, sem dados permanentes."""

from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from test_s3_t01_db import cenario_pg  # noqa: F401
from test_s4_t03_postgresql import _inserir_fechamento


def test_indices_reais_rejeitam_duplicidade(request):
    engine, ids = request.getfixturevalue("cenario_pg")
    with engine.connect() as conn:
        transacao = conn.begin()
        try:
            fechamento = _inserir_fechamento(conn, ids)
            snapshot = conn.scalar(text("""
                INSERT INTO snapshots_fechamento (
                    fechamento_id, lote_id, parametro_set_id,
                    versao_parametros, versao_metodo, entradas, resultados
                ) VALUES (:f, :l, :p, 'TESTE', 'TESTE', '{}', '{}')
                RETURNING id
            """), {"f": fechamento, "l": ids[0], "p": ids[1]})

            def inserir(status, chave):
                token = conn.scalar(text("""
                    INSERT INTO tokens_publicos (token_hash)
                    VALUES (:hash) RETURNING id
                """), {"hash": uuid4().hex * 2})
                conn.execute(text("""
                    INSERT INTO certificados (
                        lote_id, snapshot_id, token_id, status,
                        wordpress_user_id, idempotency_hash,
                        request_hash, snapshot_sha256
                    ) VALUES (:l, :s, :t, :status, 42, :chave, :hash, :hash)
                """), {
                    "l": ids[0], "s": snapshot, "t": token,
                    "status": status, "chave": chave, "hash": "a" * 64,
                })

            chave = uuid4().hex * 2
            inserir("VALIDO", chave)
            with pytest.raises(IntegrityError) as erro:
                with conn.begin_nested():
                    inserir("VALIDO", uuid4().hex * 2)
            assert erro.value.orig.diag.constraint_name == (
                "uq_certificado_valido_por_lote"
            )
            with pytest.raises(IntegrityError) as erro:
                with conn.begin_nested():
                    inserir("REVOGADO", chave)
            assert erro.value.orig.diag.constraint_name == (
                "uq_certificado_idempotencia"
            )
            inserir("REVOGADO", uuid4().hex * 2)
        finally:
            transacao.rollback()
