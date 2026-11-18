"""Duas emissoes simultaneas via API, PostgreSQL e sessoes independentes."""

import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateSchema, DropSchema

from app.db.database import obter_db
from app.main import app
from app.models import Base
from app.models.certificado import Certificado
from app.models.token_publico import TokenPublico
from test_s2_t01_api import ambiente_api  # noqa: F401
from test_s4_t02_fechamento import fechamento_api  # noqa: F401
from test_s5_t01_certificacao import emitir


@pytest.mark.parametrize("mesma_chave", [True, False])
def test_emissoes_concorrentes(request, monkeypatch, mesma_chave):
    url = os.getenv("AGROTRACER_TEST_DATABASE_URL")
    if not url:
        pytest.skip("PostgreSQL de teste nao configurado")
    assert make_url(url).database == "agrotracer_s2_t01_teste"
    cenario = request.getfixturevalue("fechamento_api")
    schema = "s5_concorrencia_" + uuid4().hex
    engine = create_engine(url)
    isolado = engine.execution_options(schema_translate_map={None: schema})
    sessao = sessionmaker(bind=isolado)
    with engine.begin() as conn:
        conn.execute(CreateSchema(schema))
    try:
        Base.metadata.create_all(isolado)
        # Copia somente o cenario sintetico da fixture, sem dados do usuario.
        with cenario[1]() as origem, isolado.begin() as destino:
            for tabela in Base.metadata.sorted_tables:
                registros = origem.execute(select(tabela)).mappings().all()
                if registros:
                    destino.execute(
                        tabela.insert(), [dict(r) for r in registros],
                    )

        def obter_teste():
            with sessao() as db:
                yield db

        app.dependency_overrides[obter_db] = obter_teste
        from app.api.v1 import certificados
        original = certificados.lote_autorizado
        barreira = Barrier(2)

        def bloquear(*args):
            barreira.wait(timeout=10)
            return original(*args)

        monkeypatch.setattr(certificados, "lote_autorizado", bloquear)
        with ThreadPoolExecutor(max_workers=2) as executor:
            futuros = [executor.submit(
                emitir, cenario, "igual" if mesma_chave else f"chave-{i}",
            ) for i in range(2)]
            respostas = [f.result(timeout=30) for f in futuros]
        assert sorted(r.status_code for r in respostas) == [201, 409]
        with sessao() as db:
            assert db.scalar(select(func.count(Certificado.id))) == 1
            assert db.scalar(select(func.count(TokenPublico.id))) == 1
    finally:
        # Nome gerado acima, restrito ao schema descartavel deste teste.
        with engine.begin() as conn:
            conn.execute(DropSchema(schema, cascade=True))
        engine.dispose()
