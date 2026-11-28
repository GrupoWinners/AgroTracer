"""Integração e concorrência reais; somente banco descartável de testes."""

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from threading import Barrier
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, select, func, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.produtor import Produtor
from app.models.fazenda import Fazenda
from app.models.lote import Lote
from app.models.parametro_set import ParametroSet
from app.models.manejo_nutricional import ManejoNutricional
from app.services.manejo_service import ErroManejo, registrar_manejo


@pytest.fixture
def cenario_pg():
    url = os.environ["AGROTRACER_TEST_DATABASE_URL"]
    assert make_url(url).database == "agrotracer_s2_t01_teste"
    engine = create_engine(url)
    with Session(engine) as db:
        produtor = Produtor(wordpress_user_id=uuid4().int % 10**12 + 1)
        fazenda = Fazenda(
            produtor=produtor, nome="Teste manejo", municipio="Teste", uf="MG"
        )
        lote = Lote(
            fazenda=fazenda, codigo_lote=uuid4().hex, status="EM_MANEJO"
        )
        conjunto = ParametroSet(
            versao=uuid4().hex, vigencia_inicio=date(2026, 1, 1)
        )
        db.add_all([lote, conjunto])
        db.flush()
        ids = (lote.id, conjunto.id, fazenda.id, produtor.id)
        db.commit()
    try:
        yield engine, ids
    finally:
        with engine.begin() as conn:
            for tabela, coluna, valor in [
                ("manejos_nutricionais", "lote_id", ids[0]),
                ("lotes", "id", ids[0]),
                ("parametro_sets", "id", ids[1]),
                ("fazendas", "id", ids[2]),
                ("produtores", "id", ids[3]),
            ]:
                conn.execute(
                    text(f"DELETE FROM {tabela} WHERE {coluna} = :id"),
                    {"id": valor},
                )
        engine.dispose()


def dados_manejo(ids, inicio=1, fim=10):
    return dict(
        lote_id=ids[0], parametro_set_id=ids[1],
        inicio=date(2026, 11, inicio), fim=date(2026, 11, fim),
        tipo_dieta="PASTAGEM",
    )


def test_service_periodos_inclusivos_e_adjacentes(cenario_pg):
    engine, ids = cenario_pg
    with Session(engine) as db:
        primeiro = registrar_manejo(db, **dados_manejo(ids))
        db.commit()
        with pytest.raises(ErroManejo) as erro:
            registrar_manejo(db, **dados_manejo(ids, 10, 15))
        assert erro.value.codigo == "MANEJO_SOBREPOSTO"
        assert erro.value.detalhes["manejo_conflitante_id"] == primeiro.id
        db.rollback()
        registrar_manejo(db, **dados_manejo(ids, 11, 11))
        db.commit()
        assert db.scalar(select(func.count()).select_from(
            ManejoNutricional
        ).where(ManejoNutricional.lote_id == ids[0])) == 2


@pytest.mark.parametrize("campo,valor,codigo", [
    ("fim", date(2026, 10, 31), "23514"),
    ("tipo_dieta", "  ", "23514"),
    ("lote_id", 999999999999999, "23503"),
    ("parametro_set_id", 999999999999999, "23503"),
])
def test_banco_rejeita_dados_invalidos(cenario_pg, campo, valor, codigo):
    engine, ids = cenario_pg
    with Session(engine) as db:
        dados = dados_manejo(ids)
        dados[campo] = valor
        db.add(ManejoNutricional(**dados))
        with pytest.raises(IntegrityError) as erro:
            db.commit()
        assert erro.value.orig.sqlstate == codigo
        db.rollback()


@pytest.mark.parametrize("usar_service", [True, False])
def test_duas_gravacoes_concorrentes_so_uma_persiste(cenario_pg, usar_service):
    engine, ids = cenario_pg
    barreira = Barrier(2)

    def gravar():
        with Session(engine) as db:
            db.execute(text("SET LOCAL statement_timeout = '8s'"))
            barreira.wait(timeout=10)
            try:
                if usar_service:
                    registrar_manejo(db, **dados_manejo(ids))
                else:
                    db.add(ManejoNutricional(**dados_manejo(ids)))
                db.commit()
                return "criado"
            except ErroManejo as erro:
                db.rollback()
                assert erro.status_code == 409
                return erro.codigo
            except IntegrityError as erro:
                db.rollback()
                assert not usar_service
                assert erro.orig.sqlstate == "23P01"
                assert erro.orig.diag.constraint_name == (
                    "ex_manejos_nutricionais_periodo"
                )
                return "MANEJO_SOBREPOSTO"

    with ThreadPoolExecutor(max_workers=2) as executor:
        futuros = [executor.submit(gravar) for _ in range(2)]
        resultados = [f.result(timeout=15) for f in futuros]
    assert sorted(resultados) == ["MANEJO_SOBREPOSTO", "criado"]
    with Session(engine) as db:
        assert db.scalar(select(func.count()).select_from(
            ManejoNutricional
        ).where(ManejoNutricional.lote_id == ids[0])) == 1


def test_exclude_e_fk_preservam_historico(cenario_pg):
    engine, ids = cenario_pg
    with Session(engine) as db:
        registrar_manejo(db, **dados_manejo(ids))
        db.commit()
        db.add(ManejoNutricional(**dados_manejo(ids, 10, 15)))
        with pytest.raises(IntegrityError) as erro:
            db.commit()
        assert erro.value.orig.sqlstate == "23P01"
        db.rollback()
        for tabela, ident in [("lotes", ids[0]), ("parametro_sets", ids[1])]:
            with pytest.raises(IntegrityError) as erro:
                db.execute(text(f"DELETE FROM {tabela} WHERE id = :id"),
                           {"id": ident})
            assert erro.value.orig.sqlstate == "23503"
            db.rollback()
