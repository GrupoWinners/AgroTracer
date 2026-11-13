"""S4-T02: endpoint autenticado e transacional de fechamento."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.bridge_dependency import exigir_usuario_wordpress
from app.core.bridge_openapi import BRIDGE_OPENAPI
from app.core.validation_route import ErrorResponse, ValidationRoute
from app.db.database import obter_db
from app.models.fazenda import Fazenda
from app.models.lote import Lote
from app.models.produtor import Produtor
from app.schemas.fechamento import FechamentoEntrada, FechamentoSaida
from app.services.fechamento_service import (
    ErroFechamento, registrar_fechamento,
)


router = APIRouter(
    prefix="/lotes", tags=["Fechamento"],
    route_class=ValidationRoute,
)


def _erro(request, status_code, codigo, mensagem):
    return JSONResponse(status_code=status_code, content={
        "error": {
            "code": codigo,
            "message": mensagem,
            "field_errors": {},
            "correlation_id": getattr(
                request.state, "correlation_id", None,
            ),
        },
    })


@router.post(
    "/{lote_id}/fechamento",
    response_model=FechamentoSaida,
    status_code=201,
    openapi_extra=BRIDGE_OPENAPI,
    responses={
        401: {"description": "Assinatura HMAC invalida"},
        403: {"description": "Usuario WordPress obrigatorio"},
        404: {"description": "Lote inexistente ou nao autorizado"},
        409: {"description": "Estado invalido ou fechamento existente",
              "model": ErrorResponse},
        422: {"description": "Manejo, abate ou fatores invalidos",
              "model": ErrorResponse},
        503: {"description": "Autenticacao indisponivel"},
    },
)
def fechar_lote(
    lote_id: int,
    dados: FechamentoEntrada,
    request: Request,
    wp_user_id: int = Depends(exigir_usuario_wordpress),
    db: Session = Depends(obter_db),
):
    try:
        lote = db.scalar(
            select(Lote)
            .join(Fazenda, Lote.fazenda_id == Fazenda.id)
            .join(Produtor, Fazenda.produtor_id == Produtor.id)
            .where(
                Lote.id == lote_id,
                Produtor.wordpress_user_id == wp_user_id,
            )
            .with_for_update(of=Lote)
        )
        if lote is None:
            raise ErroFechamento(
                404, "LOTE_NAO_ENCONTRADO",
                "Lote inexistente ou acesso nao autorizado.",
            )

        fechamento = registrar_fechamento(
            db, lote, dados, wp_user_id,
            getattr(request.state, "correlation_id", None),
        )
        resposta = FechamentoSaida(
            id=fechamento.id,
            lote_id=lote.id,
            status_lote=lote.status,
            data_abate=fechamento.data_abate,
            numero_animais_abate=fechamento.numero_animais_abate,
            parametro_set_id=fechamento.parametro_set_id,
            versao_metodo=fechamento.versao_metodo,
            emissao_total_kg_co2e=str(
                fechamento.emissao_total_kg_co2e
            ),
            intensidade_kg_co2e_kg=str(
                fechamento.intensidade_kg_co2e_kg
            ),
        )
        db.commit()
        return resposta
    except ErroFechamento as erro:
        db.rollback()
        return _erro(
            request, erro.status_code,
            erro.codigo, erro.mensagem,
        )
    except IntegrityError as erro:
        db.rollback()
        if getattr(erro.orig, "sqlstate", None) == "23505":
            return _erro(
                request, 409, "LOTE_JA_FECHADO",
                "Fechamento ja registrado.",
            )
        raise
    except Exception:
        db.rollback()
        raise
