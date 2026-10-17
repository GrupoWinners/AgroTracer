from unittest.mock import Mock

import pytest
from redis.exceptions import ConnectionError as RedisConnectionError

from app.core.nonce_store import (
    NONCE_TTL_SEGUNDOS,
    RedisIndisponivel,
    registrar_nonce,
)


NONCE_TESTE = "00112233445566778899aabbccddeeff"


def test_nonce_novo():
    cliente = Mock()
    cliente.set.return_value = True

    resultado = registrar_nonce(cliente, NONCE_TESTE)

    assert resultado is True

    cliente.set.assert_called_once_with(
        name=f"agrotracer:bridge:nonce:{NONCE_TESTE}",
        value="1",
        nx=True,
        ex=NONCE_TTL_SEGUNDOS,
    )

    assert NONCE_TTL_SEGUNDOS == 600


def test_nonce_repetido():
    cliente = Mock()
    cliente.set.return_value = False

    resultado = registrar_nonce(cliente, NONCE_TESTE)

    assert resultado is False


def test_redis_indisponivel():
    cliente = Mock()
    cliente.set.side_effect = RedisConnectionError(
        "Falha simulada de conexão"
    )

    with pytest.raises(RedisIndisponivel):
        registrar_nonce(cliente, NONCE_TESTE)
