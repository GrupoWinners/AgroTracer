from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Identity,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.parametro_set import ParametroSet


class Fator(Base):
    __tablename__ = "fatores"

    __table_args__ = (
        UniqueConstraint(
            "parametro_set_id",
            "chave",
            name="uq_fatores_set_chave",
        ),
        CheckConstraint(
            "source_type IN ("
            "'SYNTHETIC', 'PROFESSOR_APPROVED', "
            "'IPCC', 'EMBRAPA', 'OTHER')",
            name="ck_fatores_source_type",
        ),
        CheckConstraint(
            "source_type = 'SYNTHETIC' OR "
            "(source_uri IS NOT NULL "
            "AND trim(source_uri) <> '')",
            name="ck_fatores_source_uri",
        ),
        CheckConstraint(
            "trim(chave) <> ''",
            name="ck_fatores_chave",
        ),
        CheckConstraint(
            "trim(unidade) <> ''",
            name="ck_fatores_unidade",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(),
        primary_key=True,
        autoincrement=True,
    )

    parametro_set_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "parametro_sets.id",
            name="fk_fatores_parametro_set_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    chave: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    unidade: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    valor: Mapped[Decimal] = mapped_column(
        Numeric(24, 12),
        nullable=False,
    )

    source_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    source_uri: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    parametro_set: Mapped["ParametroSet"] = relationship(
        "ParametroSet",
        back_populates="fatores",
    )
