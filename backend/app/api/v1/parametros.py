"""S3-T02: ativacao administrativa de parametros."""

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Query,
)
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.admin_dependency import exigir_admin_wordpress
from app.core.bridge_openapi import BRIDGE_OPENAPI
from app.core.validation_route import ErrorResponse, ValidationRoute
from app.db.database import obter_db
from app.models.parametro_set import ParametroSet
from app.services.parametro_service import (
    ErroParametro,
    ativar_parametro_set,
)


router = APIRouter(
    prefix="/admin/parametro-sets",
    tags=["Administracao de parametros"],
    route_class=ValidationRoute,
)


class FatorSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chave: str
    unidade: str
    valor: Decimal
    source_type: str
    source_uri: str | None


class ParametroSetSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    versao: str
    status: str
    vigencia_inicio: date
    vigencia_fim: date | None
    aprovado_por: str | None
    aprovado_em: datetime | None
    fatores: list[FatorSaida]


@router.get(
    "", response_model=list[ParametroSetSaida],
    openapi_extra=BRIDGE_OPENAPI,
    responses={
        401: {"description": "HMAC inválido"},
        403: {"description": "Administrador obrigatório"},
        422: {"description": "Filtro ou paginação inválidos",
              "model": ErrorResponse},
        503: {"description": "Autenticação/administração indisponível"},
    },
)
def listar_parametro_sets(
    status: Literal["RASCUNHO", "ATIVO", "INATIVO"] | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    administrador_id: int = Depends(exigir_admin_wordpress),
    db: Session = Depends(obter_db),
):
    """Lista versões e proveniência; valores Decimal são strings JSON.

    SYNTHETIC identifica exclusivamente dados didáticos, sem fonte oficial.
    A lista de administradores vem da configuração do servidor.
    """
    consulta = select(ParametroSet).options(
        selectinload(ParametroSet.fatores)
    ).order_by(ParametroSet.id).limit(limit).offset(offset)
    if status is not None:
        consulta = consulta.where(ParametroSet.status == status)
    return db.scalars(consulta).all()


class AtivacaoParametroEntrada(BaseModel):
    justificativa: str = Field(
        min_length=1,
        max_length=500,
    )


class AtivacaoParametroSaida(BaseModel):
    id: int
    versao: str
    status: str
    aprovado_por: str
    aprovado_em: datetime


@router.post(
    "/{parametro_set_id}/ativar",
    response_model=AtivacaoParametroSaida,
    responses={
        403: {"description": "Administrador obrigatorio"},
        404: {"description": "Conjunto nao encontrado"},
        409: {"description": "Conflito de versao ou estado"},
        422: {"description": "Justificativa ou conjunto invalido"},
    },
)
def ativar_versao_parametros(
    parametro_set_id: int,
    entrada: AtivacaoParametroEntrada,
    request: Request,
    db: Session = Depends(obter_db),
    administrador_id: int = Depends(exigir_admin_wordpress),
):
    correlation_id = request.headers.get(
        "X-Correlation-ID"
    )

    if correlation_id is not None:
        correlation_id = correlation_id[:128]

    try:
        conjunto = ativar_parametro_set(
            db=db,
            parametro_set_id=parametro_set_id,
            wordpress_user_id=administrador_id,
            justificativa=entrada.justificativa,
            correlation_id=correlation_id,
        )

        resultado = AtivacaoParametroSaida(
            id=conjunto.id,
            versao=conjunto.versao,
            status=conjunto.status,
            aprovado_por=conjunto.aprovado_por,
            aprovado_em=conjunto.aprovado_em,
        )

        db.commit()
        return resultado

    except ErroParametro as erro:
        db.rollback()
        raise HTTPException(
            status_code=erro.status_code,
            detail={
                "code": erro.codigo,
                "message": erro.mensagem,
                "correlation_id": correlation_id,
            },
        ) from erro

    except IntegrityError as erro:
        db.rollback()

        if getattr(erro.orig, "sqlstate", None) == "23505":
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "PARAMETRO_SET_CONFLITO",
                    "message": (
                        "Conflito ao ativar a versao. "
                        "Atualize os dados e tente novamente."
                    ),
                    "correlation_id": correlation_id,
                },
            ) from erro

        raise

    except Exception:
        db.rollback()
        raise
