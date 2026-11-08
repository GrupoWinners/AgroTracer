import pytest
import pytest_asyncio
from datetime import date
from sqlalchemy import create_engine, text
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.api.v1.manejos import exigir_usuario_wordpress 

DB_TEST_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/agrotracer_test"

# 1. Seeding Hermético das chaves estrangeiras (escopo de sessão)
@pytest.fixture(scope="session", autouse=True)
def seed_parametro_set():
    engine = create_engine(DB_TEST_URL)
    data_hoje = date.today()
    
    with engine.connect() as conn:
        conn.execute(
            text("""
                INSERT INTO parametro_sets (id, versao, vigencia_inicio) 
                VALUES (1, 1, :vigencia_inicio) 
                ON CONFLICT (id) DO NOTHING;
            """),
            {"vigencia_inicio": data_hoje}
        )
        conn.commit()
    yield

# 2. FIXTURE DE LIMPEZA (Teardown): Trunca a tabela de manejos a cada teste
@pytest.fixture(autouse=True)
def limpar_tabela_manejos():
    """
    Garante o isolamento limpando os registros de manejos nutricionais 
    antes de cada função de teste ser executada.
    """
    engine = create_engine(DB_TEST_URL)
    with engine.connect() as conn:
        # Se no seu banco a tabela se chamar 'manejos_nutricionais' ou 'manejos', ajuste aqui
        conn.execute(text("TRUNCATE TABLE manejos_nutricionais RESTART IDENTITY CASCADE;"))
        conn.commit()
    yield

# 3. Bypass de Auth do WordPress
def mock_exigir_usuario_wordpress():
    return 1

# 4. AsyncClient HTTPX
@pytest_asyncio.fixture
async def client():
    app.dependency_overrides[exigir_usuario_wordpress] = mock_exigir_usuario_wordpress

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

@pytest.fixture
def lote_valido():
    return 1