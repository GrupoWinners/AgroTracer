import os
from urllib.parse import urlsplit


def obter_chave_bridge() -> bytes:
    segredo = os.environ.get("AGROTRACER_BRIDGE_SECRET")

    if not segredo:
        raise RuntimeError(
            "AGROTRACER_BRIDGE_SECRET não configurada."
        )

    if not segredo.isascii() or len(segredo) < 32:
        raise RuntimeError(
            "A chave do bridge possui formato inválido."
        )

    return segredo.encode("ascii")


def obter_redis_url() -> str:
    url = os.environ.get("AGROTRACER_REDIS_URL", "")

    try:
        partes = urlsplit(url)
        valido = (
            partes.scheme in ("redis", "rediss")
            and partes.hostname is not None
        )
    except ValueError:
        valido = False

    if not valido:
        raise RuntimeError(
            "AGROTRACER_REDIS_URL não configurada ou inválida."
        )

    return url
