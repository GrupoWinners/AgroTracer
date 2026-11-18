"""S5-T03: tokens de 256 bits e lookup limitado antes de acessar o banco."""

import hashlib
import re
import secrets

from sqlalchemy import select

from app.core.bridge_errors import ErroBridge
from app.models.token_publico import TokenPublico


LIMITE_CONSULTAS = 30
JANELA_SEGUNDOS = 60
_INCREMENTAR = """
local n = redis.call('INCR', KEYS[1])
if n == 1 then redis.call('EXPIRE', KEYS[1], ARGV[1]) end
return n
"""


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def emitir_token(db):
    """Nao confirma transacao. O texto original so e retornado ao emissor."""
    token = secrets.token_urlsafe(32)
    registro = TokenPublico(token_hash=hash_token(token))
    db.add(registro)
    db.flush()
    return registro, token


async def consultar_token(db, redis, token: str, endereco_cliente: str):
    """Usar IP da conexao, nunca X-Forwarded-For sem proxy confiavel.

    Contrato interno para S5-T05: nao serializar o registro retornado.
    O contador compartilhado entre workers inclui tokens malformados.
    """
    chave = "agrotracer:lookup:" + hash_token(endereco_cliente)
    try:
        quantidade = await redis.eval(
            _INCREMENTAR, 1, chave, JANELA_SEGUNDOS,
        )
        if not isinstance(quantidade, int):
            raise ValueError("Contador invalido")
    except Exception:
        raise ErroBridge(
            503, "CONSULTA_INDISPONIVEL",
            "Consulta temporariamente indisponivel.",
        ) from None
    if quantidade > LIMITE_CONSULTAS:
        raise ErroBridge(
            429, "LIMITE_CONSULTAS", "Tente novamente em um minuto.",
        )
    registro = None
    if re.fullmatch(r"[A-Za-z0-9_-]{43}", token):
        registro = db.scalar(select(TokenPublico).where(
            TokenPublico.token_hash == hash_token(token),
        ))
    if registro is None:
        raise ErroBridge(
            404, "CERTIFICADO_NAO_ENCONTRADO",
            "Certificado nao encontrado.",
        )
    return registro
