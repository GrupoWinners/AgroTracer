"""
Smoke test: apenas verifica se o fixture 'client' consegue iniciar.
Deve passar sem precisar de Redis ou PostgreSQL reais.
"""
import pytest


@pytest.mark.asyncio
async def test_client_fixture_inicia(client):
    """Verifica que o fixture client cria o AsyncClient com sucesso."""
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

