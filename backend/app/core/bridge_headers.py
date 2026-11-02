from fastapi import Request
import re
import uuid

from app.core.hmac_protocol import validar_timestamp_header


def ler_headers_bridge(request: Request) -> dict[str, str | None]:
    return {
        "signature": request.headers.get("X-AgroTracer-Signature"),
        "timestamp": request.headers.get("X-AgroTracer-Timestamp"),
        "nonce": request.headers.get("X-AgroTracer-Nonce"),
        "user_id": request.headers.get("X-AgroTracer-User-Id"),
        "correlation_id": request.headers.get("X-Correlation-ID"),
    }


CAMPOS_OBRIGATORIOS = (
    "signature",
    "timestamp",
    "nonce",
    "user_id",
    "correlation_id",
)


def headers_obrigatorios_presentes(
    headers: dict[str, str | None],
) -> bool:
    return all(
        isinstance(headers.get(campo), str)
        and bool(headers[campo].strip())
        for campo in CAMPOS_OBRIGATORIOS
    )


def validar_headers_bridge(
    headers: dict[str, str | None],
    agora: int | None = None,
) -> bool:

    if not headers_obrigatorios_presentes(headers):
        return False

    assinatura = headers.get("signature") or ""
    nonce = headers.get("nonce") or ""
    user_id = headers.get("user_id") or ""
    correlation_id = headers.get("correlation_id") or ""
    timestamp = headers.get("timestamp")

    if not re.fullmatch(r"[0-9a-f]{64}", assinatura):
        return False

    if not re.fullmatch(r"[0-9a-f]{32}", nonce):
        return False

    if not re.fullmatch(r"(0|[1-9][0-9]{0,19})", user_id):
        return False

    if len(correlation_id) != 36:
        return False

    try:
        identificador = uuid.UUID(correlation_id)
    except ValueError:
        return False

    if identificador.version != 4:
        return False

    if str(identificador) != correlation_id:
        return False

    return validar_timestamp_header(timestamp, agora)
