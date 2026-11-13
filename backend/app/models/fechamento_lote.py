"""S4-T02: dados de abate e resultado persistido por lote."""

from datetime import date
from decimal import Decimal

from sqlalchemy import (
    BigInteger, CheckConstraint, Date, ForeignKey, Identity,
    Integer, Numeric, String, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class FechamentoLote(Base):
    __tablename__ = "fechamentos_lote"

    __table_args__ = (
        UniqueConstraint("lote_id", name="uq_fechamentos_lote"),
        CheckConstraint(
            "numero_animais_abate > 0",
            name="ck_fechamento_animais_positivos",
        ),
        CheckConstraint(
            "peso_medio_abate_kg > 0",
            name="ck_fechamento_peso_positivo",
        ),
        CheckConstraint(
            "rendimento_carcaca > 0 AND rendimento_carcaca <= 1",
            name="ck_fechamento_rendimento",
        ),
        CheckConstraint(
            "emissao_total_kg_co2e >= 0 AND intensidade_kg_co2e_kg >= 0",
            name="ck_fechamento_resultados",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(), primary_key=True,
    )
    lote_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("lotes.id", ondelete="RESTRICT"),
        nullable=False,
    )
    parametro_set_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("parametro_sets.id", ondelete="RESTRICT"),
        nullable=False,
    )
    versao_metodo: Mapped[str] = mapped_column(
        String(80), nullable=False,
    )
    data_abate: Mapped[date] = mapped_column(Date, nullable=False)
    numero_animais_abate: Mapped[int] = mapped_column(
        Integer, nullable=False,
    )
    peso_medio_abate_kg: Mapped[Decimal] = mapped_column(
        Numeric(24, 12), nullable=False,
    )
    rendimento_carcaca: Mapped[Decimal] = mapped_column(
        Numeric(24, 12), nullable=False,
    )
    emissao_total_kg_co2e: Mapped[Decimal] = mapped_column(
        Numeric(38, 18), nullable=False,
    )
    intensidade_kg_co2e_kg: Mapped[Decimal] = mapped_column(
        Numeric(38, 18), nullable=False,
    )
