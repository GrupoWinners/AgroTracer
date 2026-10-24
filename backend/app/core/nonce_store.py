try:
    from redis.asyncio import Redis
    from redis.exceptions import RedisError
except ImportError:
    Redis = None

    class RedisError(Exception):
        pass


NONCE_TTL_SEGUNDOS = 660


class RedisIndisponivel(RuntimeError):
    pass


async def registrar_nonce(cliente, nonce: str) -> bool:
    if cliente is None:
        return True

    try:
        registrado = await cliente.set(
            name=f"agrotracer:bridge:nonce:{nonce}",
            value="1",
            nx=True,
            ex=NONCE_TTL_SEGUNDOS,
        )

    except RedisError as erro:
        raise RedisIndisponivel(
            "Não foi possível verificar o nonce."
        ) from erro

    return registrado is True
