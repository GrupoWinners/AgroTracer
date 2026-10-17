from fastapi import Request

from app.core.bridge_auth import verificar_hmac_requisicao
from app.core.nonce_store import RedisIndisponivel
from app.core.settings import obter_chave_bridge
from app.core.bridge_errors import ErroBridge


async def exigir_autenticacao_bridge(request: Request) -> None:
    try:
        chave = obter_chave_bridge()
        cliente_redis = request.app.state.redis_cliente

    except (RuntimeError, AttributeError):
        raise ErroBridge(
            503,
            "AUTH_SERVICE_UNAVAILABLE",
            "Serviço de autenticação indisponível.",
        ) from None

    try:
        autenticado = await verificar_hmac_requisicao(
            request=request,
            chave=chave,
            cliente_redis=cliente_redis,
        )

    except RedisIndisponivel:
        raise ErroBridge(
            503,
            "AUTH_SERVICE_UNAVAILABLE",
            "Serviço de autenticação indisponível.",
        ) from None

    if not autenticado:
        raise ErroBridge(
            401,
            "AUTH_INVALID_REQUEST",
            "Não foi possível autenticar a requisição.",
        )
