"""Verifica Lua em Redis real; CI usa instancia descartavel exclusiva."""

import asyncio
import os
from uuid import uuid4

import pytest
from redis.asyncio import Redis

from app.core.bridge_errors import ErroBridge
from app.core.rate_limit import limitar


@pytest.mark.asyncio
async def test_limite_atomico_redis_real():
    url = os.getenv("AGROTRACER_TEST_REDIS_URL")
    if not url:
        pytest.skip("Redis de teste nao configurado")
    cliente = Redis.from_url(url)
    identidade = uuid4().hex
    try:
        async def consultar():
            try:
                await limitar(cliente, "teste", identidade, 3, janela=2)
                return 200
            except ErroBridge as erro:
                return erro.status_code
        respostas = await asyncio.gather(*(consultar() for _ in range(10)))
        assert respostas.count(200) == 3
        assert respostas.count(429) == 7
        await asyncio.sleep(2.1)
        assert await consultar() == 200
    finally:
        await cliente.aclose()
