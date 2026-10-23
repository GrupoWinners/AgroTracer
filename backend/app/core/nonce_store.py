
from redis.asyncio import Redis
from redis.exceptions import RedisError


NONCE_TTL_SEGUNDOS = 660


class RedisIndisponivel(RuntimeError):
    pass


async def registrar_nonce(cliente: Redis, nonce: str) -> bool:
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
