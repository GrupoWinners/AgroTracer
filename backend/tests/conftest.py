import os
from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.bridge_dependency import exigir_usuario_wordpress
from app.db.database import obter_db
from app.main import app
from app.models import Base
from app.models.fazenda import Fazenda
from app.models.lote import Lote
from app.models.parametro_set import ParametroSet
from app.models.produtor import Produtor


@compiles(JSONB, "sqlite")
def _compilar_jsonb_sqlite(type_, compiler, **kw):
    return "TEXT"


_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(_engine, "connect")
def _preparar_sqlite(conexao, registro):
    conexao.create_function(
        "btrim", 1, lambda s: s.strip() if s is not None else ""
    )
    conexao.create_function(
        "char_length", 1, lambda s: len(s) if s is not None else 0
    )


_Session = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=_engine,
)


def _override_obter_db():
    db = _Session()
    try:
        yield db
    finally:
        db.close()


DB_TEST_URL = (
    os.getenv("AGROTRACER_TEST_DATABASE_URL")
    or os.getenv("DATABASE_URL")
)


def _criar_engine_pg(url: str):
    """Cria engine com fallback entre drivers psycopg e psycopg2."""
    args = {}
    if "psycopg2" in url:
        args = {"connect_timeout": 3}
    elif "psycopg" in url:
        args = {"timeout": 3}
    try:
        return create_engine(url, connect_args=args)
    except Exception:
        if "postgresql+psycopg2://" in url:
            alt = url.replace(
                "postgresql+psycopg2://", "postgresql+psycopg://"
            )
            return create_engine(alt)
        elif "postgresql+psycopg://" in url:
            alt = url.replace(
                "postgresql+psycopg://", "postgresql+psycopg2://"
            )
            return create_engine(alt)
        raise


@pytest.fixture(scope="session", autouse=True)
def seed_parametro_set():
    """
    Insere o registro base (id=1, versao=1, vigencia_inicio=hoje)
    respeitando as restricoes NOT NULL do PostgreSQL.
    """
    url = (
        os.getenv("AGROTRACER_TEST_DATABASE_URL")
        or os.getenv("DATABASE_URL")
        or DB_TEST_URL
    )
    if not url:
        yield
        return

    try:
        engine = _criar_engine_pg(url)
        data_hoje = date.today()

        with engine.connect() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO parametro_sets (id, versao, vigencia_inicio)
                    VALUES (1, 1, :vigencia_inicio)
                    ON CONFLICT (id) DO NOTHING;
                    """
                ),
                {"vigencia_inicio": data_hoje},
            )
            conn.commit()
    except Exception:
        pass
    yield


@pytest.fixture(autouse=True)
def limpar_tabela_manejos():
    """
    Garante idempotencia limpando a tabela de manejos nutricionais
    antes da execucao de cada teste da suite.
    """
    url = (
        os.getenv("AGROTRACER_TEST_DATABASE_URL")
        or os.getenv("DATABASE_URL")
        or DB_TEST_URL
    )
    if not url:
        yield
        return

    try:
        engine = _criar_engine_pg(url)
        with engine.connect() as conn:
            conn.execute(
                text(
                    "TRUNCATE TABLE manejos_nutricionais "
                    "RESTART IDENTITY CASCADE;"
                )
            )
            conn.commit()
    except Exception:
        pass
    yield


@pytest_asyncio.fixture(scope="function")
async def client():
    """
    Fixture assincrona com SQLite in-memory, Redis mockado e cliente HTTPX.
    """
    Base.metadata.create_all(bind=_engine)
    app.dependency_overrides[obter_db] = _override_obter_db
    app.dependency_overrides[exigir_usuario_wordpress] = lambda: 1

    with _Session() as db:
        if not db.get(ParametroSet, 1):
            db.add(
                ParametroSet(
                    id=1,
                    versao="1",
                    vigencia_inicio=date.today(),
                )
            )
        if not db.get(Produtor, 1):
            db.add(Produtor(id=1, wordpress_user_id=1))
        if not db.get(Fazenda, 1):
            db.add(
                Fazenda(
                    id=1,
                    produtor_id=1,
                    nome="Fazenda Teste",
                    municipio="Municipio Teste",
                    uf="MG",
                )
            )
        if not db.get(Lote, 1):
            db.add(
                Lote(
                    id=1,
                    fazenda_id=1,
                    codigo_lote="LOTE-TESTE-01",
                    status="EM_MANEJO",
                )
            )
        db.commit()

    redis_falso = AsyncMock()
    env_patch = patch.dict(
        os.environ,
        {"AGROTRACER_REDIS_URL": "redis://localhost:6379/0"},
    )
    redis_patch = patch("app.main.Redis.from_url", return_value=redis_falso)

    with env_patch, redis_patch:
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport, base_url="http://test"
        ) as ac:
            yield ac

    app.dependency_overrides.pop(obter_db, None)
    app.dependency_overrides.pop(exigir_usuario_wordpress, None)
    Base.metadata.drop_all(bind=_engine)


@pytest.fixture
def lote_valido():
    return 1
