from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import Request
from fastapi.responses import JSONResponse


class ErroBridge(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
    ):
        self.status_code = status_code
        self.code = code
        self.message = message


def obter_correlation_id(valor: str | None) -> str:
    if valor:
        try:
            identificador = UUID(valor)

            if identificador.version == 4 and str(identificador) == valor:
                return valor

        except ValueError:
            pass

    return str(uuid4())


async def tratar_erro_bridge(
    request: Request,
    erro: ErroBridge,
) -> JSONResponse:
    correlation_id = getattr(
        request.state,
        "correlation_id",
        None,
    )

    if correlation_id is None:
        correlation_id = obter_correlation_id(
            request.headers.get("X-Correlation-ID")
        )

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    return JSONResponse(
        status_code=erro.status_code,
        content={
            "success": False,
            "error": {
                "code": erro.code,
                "message": erro.message,
                "correlation_id": correlation_id,
                "timestamp": timestamp,
            },
        },
        headers={
            "X-Correlation-ID": correlation_id,
        },
    )
