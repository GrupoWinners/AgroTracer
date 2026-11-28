from contextlib import asynccontextmanager
import logging
from time import perf_counter

from fastapi import FastAPI, Request

try:
    from redis.asyncio import Redis
except ImportError:
    Redis = None

from app.api.v1 import api_router
from app.core.bridge_errors import (
    ErroBridge,
    obter_correlation_id,
    tratar_erro_bridge,
)
from app.core.settings import obter_redis_url
from app.core.safe_logging import ROTAS, configurar_logs


@asynccontextmanager
async def lifespan(app: FastAPI):
    configurar_logs()
    if Redis is not None:
        cliente = Redis.from_url(
            obter_redis_url(),
            socket_connect_timeout=2,
            socket_timeout=2,
        )

        try:
            await cliente.ping()
            app.state.redis_cliente = cliente
            yield
        finally:
            if hasattr(app.state, "redis_cliente"):
                del app.state.redis_cliente
            await cliente.aclose()
    else:
        yield


app = FastAPI(
    title="AgroTracer API",
    description="API backend do projeto AgroTracer",
    version="0.1.0",
    lifespan=lifespan,
)


app.add_exception_handler(
    ErroBridge,
    tratar_erro_bridge,
)


@app.middleware("http")
async def adicionar_correlation_id(request: Request, call_next):
    correlation_id = obter_correlation_id(
        request.headers.get("X-Correlation-ID")
    )

    request.state.correlation_id = correlation_id

    inicio = perf_counter()
    status_code = 500
    try:
        resposta = await call_next(request)
        status_code = resposta.status_code
    finally:
        rota = getattr(request.scope.get("route"), "path", None)
        if rota and "/api/v1" + rota in ROTAS:
            rota = "/api/v1" + rota
        logging.getLogger("agrotracer.http").info("", extra={
            "evento": (
                "request_failed" if status_code >= 500
                else "request_completed"
            ),
            "route_template": rota,
            "status_code": status_code,
            "correlation_id": correlation_id,
            "duration_ms": (perf_counter() - inicio) * 1000,
        })

    resposta.headers["X-Correlation-ID"] = correlation_id

    return resposta


app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


ROTAS.update(app.openapi()["paths"])
