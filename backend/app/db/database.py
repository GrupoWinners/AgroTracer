import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


def criar_engine() -> Engine:
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "A variável DATABASE_URL não está configurada."
        )

    return create_engine(
        database_url,
        pool_pre_ping=True,
    )


def obter_db() -> Generator[Session, None, None]:
    engine = criar_engine()
    fabrica = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    sessao = fabrica()

    try:
        yield sessao
    finally:
        sessao.close()
        engine.dispose()
