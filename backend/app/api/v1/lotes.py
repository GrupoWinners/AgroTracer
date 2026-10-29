from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.bridge_dependency import exigir_usuario_wordpress
from app.db.database import obter_db
from app.models.fazenda import Fazenda
from app.models.lote import Lote
from app.models.produtor import Produtor
from app.schemas.lote import LoteResponse
from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.schemas.lote import LoteCreate
from app.services.audit_service import registrar_auditoria
from app.domain.estados_lote import EstadoLote


router = APIRouter(prefix="/lotes", tags=["Lotes"])

# RN-04: estado inicial proposto.
# Pendente de validacao da maquina de estados pela equipe.
ESTADO_INICIAL_LOTE = EstadoLote.RASCUNHO.value


@router.post(
    "",
    response_model=LoteResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"description": "Fazenda nao encontrada ou nao autorizada"},
        409: {"description": "Codigo de lote duplicado"},
    },
)
def criar_lote(
    dados: LoteCreate,
    request: Request,
    wp_user_id: int = Depends(exigir_usuario_wordpress),
    db: Session = Depends(obter_db),
):
    """Cria um lote somente em fazenda do produtor autenticado."""

    consulta = (
        select(Fazenda)
        .join(Produtor, Fazenda.produtor_id == Produtor.id)
        .where(
            Fazenda.id == dados.fazenda_id,
            Produtor.wordpress_user_id == wp_user_id,
        )
    )

    fazenda = db.execute(consulta).scalar_one_or_none()

    if fazenda is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fazenda não encontrada ou acesso não autorizado.",
        )

    try:
        lote = Lote(
            fazenda_id=fazenda.id,
            codigo_lote=dados.codigo_lote,
            status=ESTADO_INICIAL_LOTE,
        )

        db.add(lote)
        db.flush()

        registrar_auditoria(
            db=db,
            entidade="lotes",
            acao="CRIAR_LOTE",
            entidade_id=lote.id,
            wordpress_user_id=wp_user_id,
            correlation_id=getattr(
                request.state,
                "correlation_id",
                None,
            ),
            detalhes={"codigo_lote": lote.codigo_lote},
            commit=False,
        )

        db.commit()
        db.refresh(lote)

        return lote

    except IntegrityError as erro:
        db.rollback()

        constraint = getattr(
            getattr(erro.orig, "diag", None),
            "constraint_name",
            None,
        )

        duplicado = (
            constraint == "uq_lotes_codigo_lote"
            or "UNIQUE constraint failed: lotes.codigo_lote"
            in str(erro.orig)
        )

        if duplicado:
            return JSONResponse(
                status_code=409,
                content={
                    "error": {
                        "code": "LOTE_CODIGO_DUPLICADO",
                        "message": "Já existe um lote com este código.",
                        "field_errors": {
                            "codigo_lote": "Código já cadastrado."
                        },
                        "correlation_id": getattr(
                            request.state,
                            "correlation_id",
                            None,
                        ),
                    }
                },
            )

        raise

    except Exception:
        db.rollback()
        raise


@router.get("", response_model=list[LoteResponse])
def listar_lotes(
    wp_user_id: int = Depends(exigir_usuario_wordpress),
    db: Session = Depends(obter_db),
):
    """Lista apenas lotes pertencentes ao produtor autenticado."""

    consulta = (
        select(Lote)
        .join(Fazenda, Lote.fazenda_id == Fazenda.id)
        .join(Produtor, Fazenda.produtor_id == Produtor.id)
        .where(Produtor.wordpress_user_id == wp_user_id)
        .order_by(Lote.id)
    )

    return db.execute(consulta).scalars().all()


@router.get("/{lote_id}", response_model=LoteResponse)
def detalhar_lote(
    lote_id: int,
    wp_user_id: int = Depends(exigir_usuario_wordpress),
    db: Session = Depends(obter_db),
):
    """Consulta lote com autorizacao por objeto (RN-19)."""

    consulta = (
        select(Lote)
        .join(Fazenda, Lote.fazenda_id == Fazenda.id)
        .join(Produtor, Fazenda.produtor_id == Produtor.id)
        .where(
            Lote.id == lote_id,
            Produtor.wordpress_user_id == wp_user_id,
        )
    )

    lote = db.execute(consulta).scalar_one_or_none()

    if lote is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lote não encontrado ou acesso não autorizado.",
        )

    return lote
