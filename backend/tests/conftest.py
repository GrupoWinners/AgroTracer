import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# Garantir DATABASE_URL no ambiente para a suíte de testes
if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = "postgresql+psycopg2://postgres:postgres@localhost:5432/agrotracer_test"

from app.main import app

# Injeta o override da dependência de autenticação da bridge (retorna ID int 1)
try:
    from app.core.bridge_dependency import exigir_usuario_wordpress
    app.dependency_overrides[exigir_usuario_wordpress] = lambda: 1
except ImportError:
    pass

@pytest_asyncio.fixture(scope="function")
async def client():
    """
    Fixture assíncrona oficial com ASGITransport e cliente HTTPX.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac