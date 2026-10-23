from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Identity,
    Numeric,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Talhao(Base):
    __tablename__ = "talhoes"

    __table_args__ = (
        CheckConstraint(
            "area_hectares > 0",
            name="ck_talhoes_area_hectares_positiva",
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

    area_hectares: Mapped[Decimal] = mapped_column(
        Numeric(12, 4),
        nullable=False,
    )
