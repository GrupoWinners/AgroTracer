"""Contador atomico compartilhado; falha fechada se Redis indisponivel."""

import hashlib

from app.core.bridge_errors import ErroBridge


INCREMENTAR = """
local n = redis.call('INCR', KEYS[1])
if n == 1 then redis.call('EXPIRE', KEYS[1], ARGV[1]) end
return n
"""


async def limitar(redis, grupo, identidade, limite, janela=60):
    digest = hashlib.sha256(str(identidade).encode()).hexdigest()
    try:
        quantidade = await redis.eval(
            INCREMENTAR, 1, f"agrotracer:rate:{grupo}:{digest}", janela,
        )
        if type(quantidade) is not int or quantidade < 1:
            raise ValueError("Contador invalido")
    except Exception:
        raise ErroBridge(
            503, "RATE_LIMIT_UNAVAILABLE",
            "Controle de requisicoes temporariamente indisponivel.",
        ) from None
    if quantidade > limite:
        raise ErroBridge(
            429, "RATE_LIMIT_EXCEEDED", "Aguarde um minuto e tente novamente.",
        )
