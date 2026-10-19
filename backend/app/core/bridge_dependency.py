from fastapi import Depends, Request

from app.core.bridge_auth import verificar_hmac_requisicao
from app.core.nonce_store import RedisIndisponivel
from app.core.settings import obter_chave_bridge
from app.core.bridge_errors import ErroBridge


async def exigir_autenticacao_bridge(request: Request) -> int:
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
    return int(request.headers["X-AgroTracer-User-Id"])


async def exigir_usuario_wordpress(
    wp_user_id: int = Depends(exigir_autenticacao_bridge),
) -> int:
    if wp_user_id == 0:
        raise ErroBridge(
            403,
            "AUTH_USER_REQUIRED",
            "Operação restrita a usuários WordPress.",
        )

    return wp_user_id
