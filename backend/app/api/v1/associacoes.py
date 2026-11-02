from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.bridge_dependency import exigir_usuario_wordpress
from app.db.database import obter_db
from app.schemas.associacao import (
    AssociacaoCreate,
    AssociacaoResponse,
)
from app.services.associacao_service import (
    ErroAssociacao,
    abrir_associacao,
    encerrar_associacao,
)


router = APIRouter(prefix="/lotes", tags=["Associacoes"])


def resposta_erro(request, codigo, mensagem, status_code):
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": codigo,
                "message": mensagem,
                "field_errors": {},
                "correlation_id": getattr(
                    request.state, "correlation_id", None
                ),
            }
        },
    )


@router.post(
    "/{lote_id}/animais",
    response_model=AssociacaoResponse,
    status_code=status.HTTP_201_CREATED,
)
def associar_animal(
    lote_id: int,
    dados: AssociacaoCreate,
    request: Request,
    wp_user_id: int = Depends(exigir_usuario_wordpress),
    db: Session = Depends(obter_db),
):
    try:
        associacao = abrir_associacao(
            db=db,
            wp_user_id=wp_user_id,
            lote_id=lote_id,
            animal_id=dados.animal_id,
            correlation_id=getattr(
                request.state, "correlation_id", None
            ),
        )

        db.commit()
        db.refresh(associacao)
        return associacao

    except ErroAssociacao as erro:
        db.rollback()
        return resposta_erro(
            request,
            erro.codigo,
            erro.mensagem,
            erro.status_code,
        )

    except IntegrityError as erro:
        db.rollback()

        constraint = getattr(
            getattr(erro.orig, "diag", None),
            "constraint_name",
            None,
        )

        duplicada = (
            constraint == "uq_animal_associacao_ativa"
            or "UNIQUE constraint failed: lote_animais.animal_id"
            in str(erro.orig)
        )

        if duplicada:
            return resposta_erro(
                request,
                "ASSOCIACAO_ATIVA_EXISTENTE",
                "O animal já possui uma associação ativa.",
                409,
            )

        raise

    except Exception:
        db.rollback()
        raise


@router.delete(
    "/{lote_id}/animais/{animal_id}",
    response_model=AssociacaoResponse,
)
def desassociar_animal(
    lote_id: int,
    animal_id: int,
    request: Request,
    wp_user_id: int = Depends(exigir_usuario_wordpress),
    db: Session = Depends(obter_db),
):
    try:
        associacao = encerrar_associacao(
            db=db,
            wp_user_id=wp_user_id,
            lote_id=lote_id,
            animal_id=animal_id,
            correlation_id=getattr(
                request.state, "correlation_id", None
            ),
        )

        db.commit()
        db.refresh(associacao)
        return associacao

    except ErroAssociacao as erro:
        db.rollback()
        return resposta_erro(
            request,
            erro.codigo,
            erro.mensagem,
            erro.status_code,
        )

    except Exception:
        db.rollback()
        raise
