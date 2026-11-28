from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.animal import Animal
from app.models.fazenda import Fazenda
from app.models.lote import Lote
from app.models.lote_animal import LoteAnimal
from app.models.produtor import Produtor
from app.services.audit_service import registrar_auditoria


class ErroAssociacao(Exception):
    def __init__(self, status_code, codigo, mensagem):
        self.status_code = status_code
        self.codigo = codigo
        self.mensagem = mensagem
        super().__init__(mensagem)


def validar_propriedade(
    db: Session,
    wp_user_id: int,
    lote_id: int,
    animal_id: int,
):
    lote = db.execute(
        select(Lote)
        .join(Fazenda, Lote.fazenda_id == Fazenda.id)
        .join(Produtor, Fazenda.produtor_id == Produtor.id)
        .where(
            Lote.id == lote_id,
            Produtor.wordpress_user_id == wp_user_id,
        )
    ).scalar_one_or_none()

    if lote is None:
        raise ErroAssociacao(
            404,
            "LOTE_NAO_ENCONTRADO",
            "Lote não encontrado ou acesso não autorizado.",
        )

    animal = db.execute(
        select(Animal)
        .join(Produtor, Animal.produtor_id == Produtor.id)
        .where(
            Animal.id == animal_id,
            Produtor.wordpress_user_id == wp_user_id,
        )
    ).scalar_one_or_none()

    if animal is None:
        raise ErroAssociacao(
            404,
            "ANIMAL_NAO_ENCONTRADO",
            "Animal não encontrado ou acesso não autorizado.",
        )

    return lote, animal


def abrir_associacao(
    db: Session,
    wp_user_id: int,
    lote_id: int,
    animal_id: int,
    correlation_id: str | None,
):
    lote, _ = validar_propriedade(
        db, wp_user_id, lote_id, animal_id
    )

    if lote.status == "FECHADO":
        raise ErroAssociacao(
            409,
            "LOTE_FECHADO",
            "Não é possível associar animais a um lote fechado.",
        )

    ativa = db.execute(
        select(LoteAnimal).where(
            LoteAnimal.animal_id == animal_id,
            LoteAnimal.desassociado_em.is_(None),
        )
    ).scalar_one_or_none()

    if ativa is not None:
        raise ErroAssociacao(
            409,
            "ASSOCIACAO_ATIVA_EXISTENTE",
            "O animal já possui uma associação ativa.",
        )

    associacao = LoteAnimal(
        animal_id=animal_id,
        lote_id=lote_id,
    )

    db.add(associacao)
    db.flush()

    registrar_auditoria(
        db=db,
        entidade="lote_animais",
        entidade_id=associacao.id,
        acao="ABRIR_ASSOCIACAO",
        wordpress_user_id=wp_user_id,
        correlation_id=correlation_id,
        detalhes={
            "animal_id": animal_id,
            "lote_id": lote_id,
        },
        commit=False,
    )

    return associacao


def encerrar_associacao(
    db: Session,
    wp_user_id: int,
    lote_id: int,
    animal_id: int,
    correlation_id: str | None,
):
    validar_propriedade(
        db, wp_user_id, lote_id, animal_id
    )

    associacao = db.execute(
        select(LoteAnimal)
        .where(
            LoteAnimal.lote_id == lote_id,
            LoteAnimal.animal_id == animal_id,
            LoteAnimal.desassociado_em.is_(None),
        )
        .with_for_update()
    ).scalar_one_or_none()

    if associacao is None:
        historica = db.execute(
            select(LoteAnimal.id).where(
                LoteAnimal.lote_id == lote_id,
                LoteAnimal.animal_id == animal_id,
            )
        ).first()

        if historica is not None:
            raise ErroAssociacao(
                409,
                "ASSOCIACAO_NAO_ATIVA",
                "A associação já foi encerrada.",
            )

        raise ErroAssociacao(
            404,
            "ASSOCIACAO_NAO_ENCONTRADA",
            "Associação não encontrada.",
        )

    # Encerra sem excluir a linha historica.
    associacao.desassociado_em = func.now()
    db.flush()

    registrar_auditoria(
        db=db,
        entidade="lote_animais",
        entidade_id=associacao.id,
        acao="ENCERRAR_ASSOCIACAO",
        wordpress_user_id=wp_user_id,
        correlation_id=correlation_id,
        detalhes={
            "animal_id": animal_id,
            "lote_id": lote_id,
        },
        commit=False,
    )

    return associacao
