"""S3-T03: criação autenticada de manejo e auditoria atômica."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.movimentacoes import resposta_erro
from app.core.bridge_dependency import exigir_usuario_wordpress
from app.core.bridge_openapi import BRIDGE_OPENAPI
from app.core.validation_route import ErrorResponse, ValidationRoute
from app.db.database import obter_db
from app.models.fazenda import Fazenda
from app.models.lote import Lote
from app.models.manejo_nutricional import ManejoNutricional
from app.models.produtor import Produtor
from app.schemas.manejo import ManejoCreate, ManejoResponse
from app.services.audit_service import registrar_auditoria
from app.services.manejo_service import ErroManejo, registrar_manejo


router = APIRouter(
    prefix="/lotes", tags=["Manejos nutricionais"],
    route_class=ValidationRoute,
)


@router.post(
    "/{lote_id}/manejos", response_model=ManejoResponse, status_code=201,
    openapi_extra=BRIDGE_OPENAPI,
    responses={
        401: {"description": "HMAC ausente, inválido ou nonce reutilizado"},
        403: {"description": "Usuário WordPress obrigatório"},
        404: {"description": "Lote não autorizado ou recurso inexistente"},
        409: {"description": "MANEJO_SOBREPOSTO: períodos inclusivos",
              "model": ErrorResponse},
        422: {"description": "Datas, dieta ou corpo inválidos",
              "model": ErrorResponse},
        503: {"description": "Autenticação indisponível"},
    },
)
def criar_manejo(
    lote_id: int,
    dados: ManejoCreate,
    request: Request,
    wp_user_id: int = Depends(exigir_usuario_wordpress),
    db: Session = Depends(obter_db),
):
    """Datas inclusivas. Identidade derivada exclusivamente do bridge HMAC.

    Lotes de outro produtor retornam o mesmo 404 de um lote inexistente.
    Manejo e evento de auditoria são confirmados na mesma transação.
    """
    try:
        lote = db.scalar(
            select(Lote.id)
            .join(Fazenda, Lote.fazenda_id == Fazenda.id)
            .join(Produtor, Fazenda.produtor_id == Produtor.id)
            .where(Lote.id == lote_id,
                   Produtor.wordpress_user_id == wp_user_id)
            .with_for_update(of=Lote)
        )
        if lote is None:
            raise ErroManejo(
                404, "LOTE_NAO_ENCONTRADO",
                "Lote não encontrado ou acesso não autorizado.",
            )
        manejo = registrar_manejo(db, lote_id=lote_id, **dados.model_dump())
        registrar_auditoria(
            db=db, entidade="manejos_nutricionais", acao="CRIAR_MANEJO",
            entidade_id=manejo.id, wordpress_user_id=wp_user_id,
            correlation_id=request.state.correlation_id,
            detalhes={
                "lote_id": lote_id,
                "inicio": manejo.inicio.isoformat(),
                "fim": manejo.fim.isoformat(),
                "parametro_set_id": manejo.parametro_set_id,
                "tipo_dieta": manejo.tipo_dieta,
            },
        )
        resposta = ManejoResponse.model_validate(manejo)
        db.commit()
        return resposta
    except ErroManejo as erro:
        db.rollback()
        corpo = {
            "code": erro.codigo,
            "message": erro.mensagem,
            "field_errors": {},
            "correlation_id": getattr(request.state, "correlation_id", None),
        }
        if getattr(erro, "detalhes", None):
            corpo["detalhes"] = erro.detalhes
            if "inicio" in erro.detalhes and "fim" in erro.detalhes:
                conflito_msg = (
                    f"{erro.mensagem} Período conflitante: "
                    f"{erro.detalhes['inicio']} a {erro.detalhes['fim']}."
                )
                corpo["message"] = conflito_msg
        return JSONResponse(
            status_code=erro.status_code, content={"error": corpo},
        )
    except Exception:
        db.rollback()
        raise


@router.get(
    "/{lote_id}/manejos", response_model=list[ManejoResponse],
    openapi_extra=BRIDGE_OPENAPI,
    responses={
        401: {"description": "HMAC ausente, inválido ou nonce reutilizado"},
        403: {"description": "Usuário WordPress obrigatório"},
        404: {"description": "Lote não autorizado ou recurso inexistente",
              "model": ErrorResponse},
        503: {"description": "Autenticação indisponível"},
    },
)
def listar_manejos(
    lote_id: int,
    request: Request,
    wp_user_id: int = Depends(exigir_usuario_wordpress),
    db: Session = Depends(obter_db),
):
    """Lista manejos ordenados cronologicamente por data de início.

    Lotes de outro produtor retornam o mesmo 404 de um lote inexistente.
    """
    lote = db.scalar(
        select(Lote.id)
        .join(Fazenda, Lote.fazenda_id == Fazenda.id)
        .join(Produtor, Fazenda.produtor_id == Produtor.id)
        .where(
            Lote.id == lote_id,
            Produtor.wordpress_user_id == wp_user_id,
        )
    )
    if lote is None:
        return resposta_erro(
            request, 404, "LOTE_NAO_ENCONTRADO",
            "Lote não encontrado ou acesso não autorizado.",
        )

    manejos = db.scalars(
        select(ManejoNutricional)
        .where(ManejoNutricional.lote_id == lote_id)
        .order_by(ManejoNutricional.inicio.asc(), ManejoNutricional.id.asc())
    ).all()

    return [ManejoResponse.model_validate(m) for m in manejos]
