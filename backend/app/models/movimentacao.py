from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Movimentacao(Base):
    __tablename__ = "movimentacoes"

    __table_args__ = (
        CheckConstraint(
            "(animal_id IS NOT NULL) <> (lote_id IS NOT NULL)",
            name="ck_movimentacoes_alvo_xor",
        ),
        CheckConstraint(
            "origem_talhao_id IS NULL "
            "OR destino_talhao_id IS NULL "
            "OR origem_talhao_id <> destino_talhao_id",
            name="ck_movimentacoes_origem_destino",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(),
        primary_key=True,
        autoincrement=True,
    )

    animal_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "animais.id",
            name="fk_movimentacoes_animal_id",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    lote_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "lotes.id",
            name="fk_movimentacoes_lote_id",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    origem_talhao_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "talhoes.id",
            name="fk_movimentacoes_origem_talhao_id",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    destino_talhao_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "talhoes.id",
            name="fk_movimentacoes_destino_talhao_id",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    tipo: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    data_hora: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    observacao: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
