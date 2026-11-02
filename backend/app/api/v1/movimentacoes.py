from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.bridge_dependency import exigir_usuario_wordpress
from app.db.database import obter_db
from app.schemas.movimentacao import (
    MovimentacaoCreate,
    MovimentacaoResponse,
)
from app.services.movimentacao_service import (
    ErroMovimentacao,
    criar_movimentacao,
)


router = APIRouter(
    prefix="/movimentacoes",
    tags=["Movimentacoes"],
)


def resposta_erro(request, status_code, codigo, mensagem):
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": codigo,
                "message": mensagem,
                "field_errors": {},
                "correlation_id": getattr(
                    request.state,
                    "correlation_id",
                    None,
                ),
            }
        },
    )


@router.post(
    "",
    response_model=MovimentacaoResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"description": "Recurso nao encontrado ou nao autorizado"},
        409: {"description": "Movimentacao fora de ordem"},
        422: {"description": "Dados ou alvo invalidos"},
    },
)
def registrar_movimentacao(
    dados: MovimentacaoCreate,
    request: Request,
    wp_user_id: int = Depends(exigir_usuario_wordpress),
    db: Session = Depends(obter_db),
):
    try:
        movimentacao = criar_movimentacao(
            db=db,
            dados=dados,
            wp_user_id=wp_user_id,
            correlation_id=getattr(
                request.state,
                "correlation_id",
                None,
            ),
        )

        db.commit()
        db.refresh(movimentacao)
        return movimentacao

    except ErroMovimentacao as erro:
        db.rollback()

        return resposta_erro(
            request,
            erro.status_code,
            erro.codigo,
            erro.mensagem,
        )

    except IntegrityError as erro:
        db.rollback()

        constraint = getattr(
            getattr(erro.orig, "diag", None),
            "constraint_name",
            None,
        )

        if constraint == "ck_movimentacoes_alvo_xor":
            return resposta_erro(
                request,
                422,
                "MOVIMENTACAO_ALVO_INVALIDO",
                "Informe exatamente um animal ou lote.",
            )

        if constraint == "ck_movimentacoes_origem_destino":
            return resposta_erro(
                request,
                422,
                "MOVIMENTACAO_ORIGEM_DESTINO_IGUAIS",
                "Origem e destino nao podem ser iguais.",
            )

        if constraint and constraint.startswith("fk_movimentacoes_"):
            return resposta_erro(
                request,
                404,
                "RECURSO_NAO_ENCONTRADO",
                "Recurso nao encontrado ou indisponivel.",
            )

        raise

    except Exception:
        db.rollback()
        raise
