from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.bridge_dependency import exigir_usuario_wordpress
from app.db.database import obter_db
from app.models.animal import Animal
from app.models.produtor import Produtor
from app.schemas.animal import AnimalCreate, AnimalResponse
from app.services.audit_service import registrar_auditoria


router = APIRouter(prefix="/animais", tags=["Animais"])


@router.post(
    "",
    response_model=AnimalResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"description": "Identificador de animal duplicado"},
    },
)
def criar_animal(
    dados: AnimalCreate,
    request: Request,
    wp_user_id: int = Depends(exigir_usuario_wordpress),
    db: Session = Depends(obter_db),
):
    try:
        # Identidade derivada do WordPress autenticado.
        produtor = db.execute(
            select(Produtor).where(
                Produtor.wordpress_user_id == wp_user_id
            )
        ).scalar_one_or_none()

        if produtor is None:
            produtor = Produtor(wordpress_user_id=wp_user_id)
            db.add(produtor)
            db.flush()

        # RN-05: identificador unico.
        # ADR-003: nao existe animais.lote_id.
        animal = Animal(
            produtor_id=produtor.id,
            identificador=dados.identificador,
            rfid=dados.rfid,
            data_nascimento_estimada=dados.data_nascimento_estimada,
        )

        db.add(animal)
        db.flush()

        # Auditoria na mesma transacao do cadastro.
        registrar_auditoria(
            db=db,
            entidade="animais",
            acao="CRIAR_ANIMAL",
            entidade_id=animal.id,
            wordpress_user_id=wp_user_id,
            correlation_id=getattr(
                request.state, "correlation_id", None
            ),
            detalhes={"identificador": animal.identificador},
            commit=False,
        )

        db.commit()
        db.refresh(animal)
        return animal

    except IntegrityError as erro:
        db.rollback()

        constraint = getattr(
            getattr(erro.orig, "diag", None),
            "constraint_name",
            None,
        )

        duplicado = (
            constraint == "uq_animais_identificador"
            or "UNIQUE constraint failed: animais.identificador"
            in str(erro.orig)
        )

        if duplicado:
            return JSONResponse(
                status_code=409,
                content={
                    "error": {
                        "code": "ANIMAL_IDENTIFICADOR_DUPLICADO",
                        "message": (
                            "Já existe um animal com este identificador."
                        ),
                        "field_errors": {
                            "identificador": "Identificador já cadastrado."
                        },
                        "correlation_id": getattr(
                            request.state, "correlation_id", None
                        ),
                    }
                },
            )

        raise

    except Exception:
        db.rollback()
        raise
