from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    func,
    text,
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.animal import Animal
    from app.models.lote import Lote


class LoteAnimal(Base):
    __tablename__ = "lote_animais"

    __table_args__ = (
        CheckConstraint(
            "desassociado_em IS NULL "
            "OR desassociado_em >= associado_em",
            name="ck_lote_animais_periodo_valido",
        ),
        Index(
            "uq_animal_associacao_ativa",
            "animal_id",
            unique=True,
            postgresql_where=text("desassociado_em IS NULL"),
            sqlite_where=text("desassociado_em IS NULL"),
        ),
    )
    animal: Mapped["Animal"] = relationship(
        "Animal",
        back_populates="associacoes_lote",
    )

    lote: Mapped["Lote"] = relationship(
        "Lote",
        back_populates="associacoes_animais",
    )

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(),
        primary_key=True,
        autoincrement=True,
    )

    animal_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "animais.id",
            name="fk_lote_animais_animal_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    lote_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "lotes.id",
            name="fk_lote_animais_lote_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    associado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    desassociado_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
