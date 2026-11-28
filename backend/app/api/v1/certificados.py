"""Emissao autenticada e atomica, sem persistir o token original."""

from fastapi import APIRouter, Depends, Header, Request, Response
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.v1.fechamentos import _erro
from app.core.bridge_dependency import exigir_usuario_wordpress
from app.core.bridge_openapi import BRIDGE_OPENAPI
from app.core.validation_route import ErrorResponse, ValidationRoute
from app.db.database import obter_db
from app.models.fazenda import Fazenda
from app.models.lote import Lote
from app.models.produtor import Produtor
from app.schemas.fechamento import FechamentoEntrada
from app.services.certificacao_service import certificar
from app.services.fechamento_service import ErroFechamento


router = APIRouter(tags=["Certificados"], route_class=ValidationRoute)


class CertificadoSaida(BaseModel):
    id: int
    lote_id: int
    status: str
    snapshot_sha256: str
    token: str


def lote_autorizado(db, lote_id, usuario):
    lote = db.scalar(
        select(Lote).join(Fazenda).join(Produtor).where(
            Lote.id == lote_id, Produtor.wordpress_user_id == usuario,
        ).with_for_update(of=Lote)
    )
    if lote is None:
        raise ErroFechamento(
            404, "LOTE_NAO_ENCONTRADO",
            "Lote inexistente ou acesso nao autorizado.",
        )
    return lote


@router.post(
    "/lotes/{lote_id}/certificar", status_code=201,
    response_model=CertificadoSaida, openapi_extra=BRIDGE_OPENAPI,
    responses={
        401: {"description": "HMAC invalido"},
        403: {"description": "Usuario obrigatorio"},
        404: {"description": "Lote inexistente ou nao autorizado"},
        409: {"description": "Repeticao controlada ou conflito",
              "model": ErrorResponse},
        422: {"description": "Entrada ou chave invalida",
              "model": ErrorResponse},
    },
)
def emitir_certificado(
    lote_id: int, dados: FechamentoEntrada, request: Request,
    response: Response,
    idempotency_key: str = Header(
        min_length=1, max_length=128, pattern=r"^[\x21-\x7e]+$",
        description="Chave unica por usuario; repeticoes retornam 409.",
    ),
    usuario: int = Depends(exigir_usuario_wordpress),
    db: Session = Depends(obter_db),
):
    try:
        lote = lote_autorizado(db, lote_id, usuario)
        certificado, token = certificar(
            db, lote, dados, usuario, idempotency_key,
            getattr(request.state, "correlation_id", None),
        )
        saida = CertificadoSaida(
            id=certificado.id, lote_id=lote.id, status=certificado.status,
            snapshot_sha256=certificado.snapshot_sha256, token=token,
        )
        db.commit()
        response.headers["Cache-Control"] = "no-store"
        return saida
    except ErroFechamento as erro:
        db.rollback()
        return _erro(request, erro.status_code, erro.codigo, erro.mensagem)
    except IntegrityError as erro:
        db.rollback()
        if getattr(erro.orig, "sqlstate", None) == "23505":
            return _erro(
                request, 409, "CERTIFICACAO_CONFLITANTE",
                "Emissao concorrente. Consulte o certificado existente.",
            )
        raise
    except Exception:
        db.rollback()
        raise
