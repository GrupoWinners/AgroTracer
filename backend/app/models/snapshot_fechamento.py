"""S4-T03: snapshot imutavel de fechamento."""

from datetime import datetime

from sqlalchemy import (
    BigInteger, DateTime, ForeignKey, Identity, Integer,
    String, UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SnapshotFechamento(Base):
    __tablename__ = "snapshots_fechamento"

    __table_args__ = (
        UniqueConstraint(
            "fechamento_id", name="uq_snapshots_fechamento",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(), primary_key=True,
    )
    fechamento_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("fechamentos_lote.id", ondelete="RESTRICT"),
        nullable=False,
    )
    lote_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("lotes.id", ondelete="RESTRICT"),
        nullable=False,
    )
    parametro_set_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("parametro_sets.id", ondelete="RESTRICT"),
        nullable=False,
    )
    versao_parametros: Mapped[str] = mapped_column(
        String(80), nullable=False,
    )
    versao_metodo: Mapped[str] = mapped_column(
        String(80), nullable=False,
    )
    entradas: Mapped[dict] = mapped_column(JSONB, nullable=False)
    resultados: Mapped[dict] = mapped_column(JSONB, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
