from redis import Redis
from redis.exceptions import RedisError


NONCE_TTL_SEGUNDOS = 600


class RedisIndisponivel(RuntimeError):
    pass


def registrar_nonce(cliente: Redis, nonce: str) -> bool:
    try:
        registrado = cliente.set(
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
