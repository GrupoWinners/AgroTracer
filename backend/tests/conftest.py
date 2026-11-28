from unittest.mock import AsyncMock
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, event
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.bridge_dependency import exigir_usuario_wordpress
from app.db.database import obter_db
from app.main import app
from app.models import Base


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


@pytest_asyncio.fixture(scope="function")
async def client():
    """
    Fixture assincrona com SQLite in-memory e cliente HTTPX.
    """
    Base.metadata.create_all(bind=_engine)
    app.state.redis_cliente = AsyncMock()
    app.dependency_overrides[obter_db] = _override_obter_db
    app.dependency_overrides[exigir_usuario_wordpress] = lambda: 1

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.pop(obter_db, None)
    app.dependency_overrides.pop(exigir_usuario_wordpress, None)
    Base.metadata.drop_all(bind=_engine)
