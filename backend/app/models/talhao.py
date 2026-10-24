from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Identity,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.fazenda import Fazenda


class Talhao(Base):
    __tablename__ = "talhoes"

    __table_args__ = (
        CheckConstraint(
            "area_hectares > 0",
            name="ck_talhoes_area_hectares_positiva",
        ),
        CheckConstraint(
            "btrim(identificador) <> ''",
            name="ck_talhoes_identificador_obrigatorio",
        ),
        UniqueConstraint(
            "fazenda_id",
            "identificador",
            name="uq_talhoes_fazenda_identificador",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True,
    )

    fazenda_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "fazendas.id",
            name="fk_talhoes_fazenda_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    identificador: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    area_hectares: Mapped[Decimal] = mapped_column(
        Numeric(12, 4),
        nullable=False,
    )

    fazenda: Mapped["Fazenda"] = relationship(
        "Fazenda",
        back_populates="talhoes",
    )
