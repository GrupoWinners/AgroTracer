import asyncio
import pytest
from httpx import AsyncClient, ASGITransport

try:
    from app.main import app
except ModuleNotFoundError:
    from main import app

@pytest.fixture(scope="session")
def event_loop():
    """Cria um event loop unico para toda a sessao de testes."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def client():
    """Fixture global para simular requisicoes assincronas a API FastAPI."""
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://testserver"
    ) as ac:
        yield ac
