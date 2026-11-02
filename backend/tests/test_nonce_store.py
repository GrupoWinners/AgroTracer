import asyncio
from unittest.mock import AsyncMock
from app.core.hmac_protocol import validar_timestamp
import pytest
from redis.exceptions import ConnectionError as RedisConnectionError

from app.core.nonce_store import (
    NONCE_TTL_SEGUNDOS,
    RedisIndisponivel,
    registrar_nonce,
)


NONCE_TESTE = "00112233445566778899aabbccddeeff"


def test_nonce_novo():
    cliente = AsyncMock()
    cliente.set.return_value = True

    resultado = asyncio.run(
        registrar_nonce(cliente, NONCE_TESTE)
    )

    assert resultado is True

    cliente.set.assert_called_once_with(
        name=f"agrotracer:bridge:nonce:{NONCE_TESTE}",
        value="1",
        nx=True,
        ex=NONCE_TTL_SEGUNDOS,
    )

    assert NONCE_TTL_SEGUNDOS == 660


def test_nonce_repetido():
    cliente = AsyncMock()
    cliente.set.return_value = False

    resultado = asyncio.run(
        registrar_nonce(cliente, NONCE_TESTE)
    )

    assert resultado is False


def test_redis_indisponivel():
    cliente = AsyncMock()
    cliente.set.side_effect = RedisConnectionError(
        "Falha simulada de conexão"
    )

    with pytest.raises(RedisIndisponivel):
        asyncio.run(
            registrar_nonce(cliente, NONCE_TESTE)
        )


def test_nonce_cliente_none():
    with pytest.raises(RedisIndisponivel):
        asyncio.run(
            registrar_nonce(None, NONCE_TESTE)
        )


def test_ttl_nonce_cobre_janela_timestamp():
    primeiro_recebimento = 1800000000

    timestamp = primeiro_recebimento + 300

    ultimo_recebimento_valido = timestamp + 300

    assert validar_timestamp(
        timestamp,
        primeiro_recebimento,
    ) is True

    assert validar_timestamp(
        timestamp,
        ultimo_recebimento_valido,
    ) is True

    tempo_total = (
        ultimo_recebimento_valido - primeiro_recebimento
    )

    assert NONCE_TTL_SEGUNDOS > tempo_total
