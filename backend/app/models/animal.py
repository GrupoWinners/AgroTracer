from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Date,
    ForeignKey,
    Identity,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.produtor import Produtor
    from app.models.lote_animal import LoteAnimal


class Animal(Base):
    __tablename__ = "animais"

    __table_args__ = (
        UniqueConstraint(
            "identificador",
            name="uq_animais_identificador",
        ),
    )
    associacoes_lote: Mapped[list["LoteAnimal"]] = relationship(
        "LoteAnimal",
        back_populates="animal",
    )

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(),
        primary_key=True,
        autoincrement=True,
    )

    produtor_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "produtores.id",
            name="fk_animais_produtor_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    identificador: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    rfid: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
    )

    data_nascimento_estimada: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    produtor: Mapped["Produtor"] = relationship(
        "Produtor",
        back_populates="animais",
    )
