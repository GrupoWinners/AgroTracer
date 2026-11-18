from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.bridge_errors import ErroBridge
from app.models.token_publico import TokenPublico
from app.services.token_service import (
    consultar_token, emitir_token, hash_token,
)
from test_s2_t01_api import ambiente_api  # noqa: F401


def test_tokens_aleatorios_unicos_e_apenas_hash(request):
    _, sessao = request.getfixturevalue("ambiente_api")
    with sessao() as db:
        tokens = [emitir_token(db)[1] for _ in range(100)]
        db.commit()
        assert len(set(tokens)) == 100
        assert all(len(token) == 43 for token in tokens)
        hashes = set(db.scalars(select(TokenPublico.token_hash)))
        assert hashes == {hash_token(token) for token in tokens}
        assert not hashes.intersection(tokens)
        db.add(TokenPublico(token_hash=hash_token(tokens[0])))
        with pytest.raises(IntegrityError):
            db.flush()


@pytest.mark.asyncio
async def test_lookup_hash_e_limite_compartilhado(request):
    _, sessao = request.getfixturevalue("ambiente_api")
    redis = AsyncMock()
    redis.eval.side_effect = [1, 31]
    with sessao() as db:
        registro, token = emitir_token(db)
        assert await consultar_token(db, redis, token, "cliente") == registro
        with pytest.raises(ErroBridge) as erro:
            await consultar_token(db, redis, token, "cliente")
        assert erro.value.status_code == 429
        assert redis.eval.call_args_list[0] == redis.eval.call_args_list[1]
        assert token not in str(redis.eval.call_args)


@pytest.mark.asyncio
@pytest.mark.parametrize("token", ["invalido", "A" * 43, "x" * 10000])
async def test_inexistente_generico_e_tambem_limitado(token):
    db = Mock()
    db.scalar.return_value = None
    redis = AsyncMock()
    redis.eval.return_value = 1
    with pytest.raises(ErroBridge) as erro:
        await consultar_token(db, redis, token, "cliente")
    assert erro.value.status_code == 404
    assert erro.value.message == "Certificado nao encontrado."
    redis.eval.assert_awaited_once()


@pytest.mark.asyncio
async def test_redis_indisponivel_nao_libera_lookup():
    db = Mock()
    redis = AsyncMock()
    redis.eval.side_effect = ConnectionError()
    with pytest.raises(ErroBridge) as erro:
        await consultar_token(db, redis, "A" * 43, "cliente")
    assert erro.value.status_code == 503
    db.scalar.assert_not_called()
