from typing import Any

from fastapi import Request

try:
    from redis.asyncio import Redis
except ImportError:
    Redis = Any

from app.core.bridge_headers import (
    ler_headers_bridge,
    validar_headers_bridge,
)
from app.core.hmac_protocol import (
    build_canonical_string,
    validar_assinatura,
)
from app.core.nonce_store import registrar_nonce


async def verificar_hmac_requisicao(
    request: Request,
    chave: bytes,
    cliente_redis: Any,
    agora: int | None = None,
) -> bool:
    headers = ler_headers_bridge(request)

    if not validar_headers_bridge(headers, agora):
        return False

    raw_path = request.scope.get("raw_path")

    if not isinstance(raw_path, bytes):
        return False

    try:
        path_with_query = raw_path.decode("ascii")
        query_string = request.scope["query_string"].decode("ascii")

        if query_string:
            path_with_query += f"?{query_string}"

        corpo = await request.body()

        canonical = build_canonical_string(
            method=request.method,
            path_with_query=path_with_query,
            timestamp=int(headers["timestamp"]),
            nonce=headers["nonce"],
            wp_user_id=int(headers["user_id"]),
            body=corpo,
        )
    except (UnicodeDecodeError, ValueError, TypeError):
        return False

    assinatura_valida = validar_assinatura(
        canonical,
        chave,
        headers["signature"],
    )

    if not assinatura_valida:
        return False

    return await registrar_nonce(
        cliente_redis,
        headers["nonce"],
    )
