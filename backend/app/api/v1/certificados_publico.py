"""S5-T05: endpoint publico de verificacao de certificado via token opaco."""

from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.orm import Session

from app.core.bridge_errors import ErroBridge
from app.core.validation_route import ErrorResponse, ValidationRoute
from app.db.database import obter_db
from app.schemas.certificado_publico import CertificadoPublicoSaida
from app.services.certificado_publico_service import (
    consultar_certificado_publico,
    obter_ip_cliente,
)

router = APIRouter(tags=["Certificados"], route_class=ValidationRoute)


@router.get(
    "/certificados/publico",
    response_model=CertificadoPublicoSaida,
    responses={
        404: {
            "description": "Certificado nao encontrado (RN-13)",
            "model": ErrorResponse,
        },
        409: {
            "description": "Integridade do snapshot comprometida",
            "model": ErrorResponse,
        },
        429: {
            "description": "Limite de consultas por IP excedido",
            "model": ErrorResponse,
        },
        503: {
            "description": "Servico de consulta indisponivel",
            "model": ErrorResponse,
        },
    },
)
async def verificar_certificado_publico(
    request: Request,
    response: Response,
    token: str = Query(
        default="",
        description="Token opaco publico recebido no link ou QR Code.",
    ),
    db: Session = Depends(obter_db),
):
    redis_cliente = getattr(request.app.state, "redis_cliente", None)
    if redis_cliente is None:
        raise ErroBridge(
            503,
            "CONSULTA_INDISPONIVEL",
            "Consulta temporariamente indisponivel.",
        )

    ip_cliente = obter_ip_cliente(request)
    dto = await consultar_certificado_publico(
        db, redis_cliente, token, ip_cliente
    )
    response.headers["Cache-Control"] = "no-store"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Robots-Tag"] = "noindex, nofollow"
    return dto
