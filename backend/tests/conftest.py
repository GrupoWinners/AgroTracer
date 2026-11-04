import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

# 1. Override de dependências do FastAPI
app.dependency_overrides = {}

# 2. Bypass de Middleware de Autenticação / Bridge Error para ambiente de teste
@app.middleware("http")
async def bypass_auth_middleware_for_tests(request, call_next):
    # Injeta contexto simulado para requisições de teste
    request.state.user = {"id": 1, "role": "admin", "email": "qa@agrotracer.com"}
    response = await call_next(request)
    return response

@pytest_asyncio.fixture(scope="function")
async def client():
    """
    Fixture assíncrona que disponibiliza o AsyncClient do HTTPX 
    com o transporte ASGI ativo.
    """
    transport = ASGITransport(app=app)
    headers = {
        "Authorization": "Bearer token-teste-qa-sprint2",
        "Content-Type": "application/json"
    }
    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as ac:
        yield ac