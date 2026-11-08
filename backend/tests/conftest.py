import pytest
import pytest_asyncio
from datetime import date
from sqlalchemy import create_engine, text
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.api.v1.manejos import exigir_usuario_wordpress

DB_TEST_URL = (
    "postgresql+psycopg2://postgres:postgres@localhost:5432/agrotracer_test"
)


@pytest.fixture(scope="session", autouse=True)
def seed_parametro_set():
    """
    Insere o registro base (id=1, versao=1, vigencia_inicio=hoje)
    respeitando as restricoes NOT NULL do PostgreSQL.
    """
    engine = create_engine(DB_TEST_URL)
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
    yield


@pytest.fixture(autouse=True)
def limpar_tabela_manejos():
    """
    Garante idempotencia limpando a tabela de manejos nutricionais
    antes da execucao de cada teste da suite.
    """
    engine = create_engine(DB_TEST_URL)
    with engine.connect() as conn:
        conn.execute(
            text(
                "TRUNCATE TABLE manejos_nutricionais "
                "RESTART IDENTITY CASCADE;"
            )
        )
        conn.commit()
    yield


def mock_exigir_usuario_wordpress():
    """Bypass da dependência do servico de Auth externa."""
    return 1


@pytest_asyncio.fixture
async def client():
    """Fixture de cliente assincrono HTTPX."""
    app.dependency_overrides[exigir_usuario_wordpress] = (
        mock_exigir_usuario_wordpress
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def lote_valido():
    return 1
