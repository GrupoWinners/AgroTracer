"""
Verifica isoladamente se o AsyncClient consegue iniciar com Redis mockado.
Usar: python backend/tests/_debug_client.py
"""
import asyncio
import os
import sys

sys.path.insert(0, "backend")

from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient


async def main():
    os.environ["AGROTRACER_SECRET_KEY"] = "test-secret-key-32-chars-minimum!"
    print("1. Importando app...")
    from app.main import app  # noqa: F401

    print("2. Configurando patches...")
    redis_falso = AsyncMock()
    env_patch = patch.dict(
        os.environ,
        {"AGROTRACER_REDIS_URL": "redis://localhost:6379/0"},
    )
    redis_patch = patch("app.main.Redis.from_url", return_value=redis_falso)

    print("3. Entrando no context manager...")
    with env_patch, redis_patch:
        print("   - env e redis patchados")
        transport = ASGITransport(app=app)
        print("   - transport criado, iniciando AsyncClient...")
        try:
            async with asyncio.timeout(10):
                async with AsyncClient(
                    transport=transport, base_url="http://test"
                ) as ac:
                    print("   - AsyncClient iniciado!")
                    resp = await ac.get("/health")
                    print(f"   - GET /health: {resp.status_code} {resp.json()}")
        except TimeoutError:
            print("TIMEOUT: AsyncClient nao iniciou em 10 segundos!")
        except Exception as e:
            print(f"ERRO: {type(e).__name__}: {e}")

    print("4. Done.")


asyncio.run(main())

