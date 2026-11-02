import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from threading import Event
from uuid import uuid4

import pytest
from sqlalchemy import (
    create_engine,
    delete,
    func,
    insert,
    select,
)
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.models.animal import Animal
from app.models.auditoria_evento import AuditoriaEvento
from app.models.movimentacao import Movimentacao
from app.models.produtor import Produtor
from app.schemas.movimentacao import MovimentacaoCreate
from app.services.movimentacao_service import (
    ErroMovimentacao,
    criar_movimentacao,
)


def test_concorrencia_respeita_cronologia():
    url = os.getenv("AGROTRACER_TEST_DATABASE_URL")

    if not url:
        pytest.skip("PostgreSQL de teste nao configurado.")

    assert make_url(url).database == "agrotracer_s2_t01_teste"

    engine = create_engine(url)
    marcador = uuid4().hex

    with engine.begin() as conn:
        wp_user_id = uuid4().int % 9000000000 + 1

        produtor_id = conn.execute(
            insert(Produtor)
            .values(wordpress_user_id=wp_user_id)
            .returning(Produtor.id)
        ).scalar_one()

        animal_id = conn.execute(
            insert(Animal)
            .values(
                produtor_id=produtor_id,
                identificador=f"CONCORRENCIA-{marcador}",
            )
            .returning(Animal.id)
        ).scalar_one()

    primeira_pronta = Event()
    segunda_iniciada = Event()

    def registrar_primeira():
        dados = MovimentacaoCreate(
            animal_id=animal_id,
            tipo="TRANSFERENCIA",
            data_hora=datetime(
                2027, 2, 10, 12, 0,
                tzinfo=timezone.utc,
            ),
        )

        with Session(engine) as db:
            movimento = criar_movimentacao(
                db, dados, wp_user_id
            )
            movimento_id = movimento.id

            # Mantem a transacao aberta enquanto
            # a segunda operacao e iniciada.
            primeira_pronta.set()

            assert segunda_iniciada.wait(timeout=10)
            db.commit()

            return movimento_id

    def registrar_anterior():
        assert primeira_pronta.wait(timeout=10)

        dados = MovimentacaoCreate(
            animal_id=animal_id,
            tipo="TRANSFERENCIA",
            data_hora=datetime(
                2027, 2, 9, 12, 0,
                tzinfo=timezone.utc,
            ),
        )

        segunda_iniciada.set()

        with Session(engine) as db:
            try:
                criar_movimentacao(
                    db, dados, wp_user_id
                )
            except ErroMovimentacao as erro:
                db.rollback()
                return erro.codigo

            db.commit()
            return "INSERIDA"

    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            primeira = pool.submit(registrar_primeira)
            segunda = pool.submit(registrar_anterior)

            movimento_id = primeira.result(timeout=20)
            resultado = segunda.result(timeout=20)

        assert movimento_id > 0
        assert resultado == "MOVIMENTACAO_FORA_DE_ORDEM"

        with Session(engine) as db:
            quantidade = db.scalar(
                select(func.count(Movimentacao.id))
                .where(Movimentacao.animal_id == animal_id)
            )

            assert quantidade == 1

    finally:
        # Limpa somente os registros criados pelo teste.
        with engine.begin() as conn:
            ids = conn.scalars(
                select(Movimentacao.id)
                .where(Movimentacao.animal_id == animal_id)
            ).all()

            if ids:
                conn.execute(
                    delete(AuditoriaEvento).where(
                        AuditoriaEvento.entidade
                        == "movimentacoes",
                        AuditoriaEvento.entidade_id.in_(ids),
                    )
                )

            conn.execute(
                delete(Movimentacao).where(
                    Movimentacao.animal_id == animal_id
                )
            )

            conn.execute(
                delete(Animal).where(
                    Animal.id == animal_id
                )
            )

            conn.execute(
                delete(Produtor).where(
                    Produtor.id == produtor_id
                )
            )

        engine.dispose()
