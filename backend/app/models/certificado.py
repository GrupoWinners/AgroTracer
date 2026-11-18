"""Certificado vinculado ao snapshot imutavel e token opaco."""

from datetime import datetime

from sqlalchemy import (
    BigInteger, CheckConstraint, DateTime, ForeignKey, Identity,
    Index, Integer, String, UniqueConstraint, func, text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Certificado(Base):
    __tablename__ = "certificados"
    __table_args__ = (
        Index(
            "uq_certificado_valido_por_lote", "lote_id", unique=True,
            postgresql_where=text("status = 'VALIDO'"),
            sqlite_where=text("status = 'VALIDO'"),
        ),
        UniqueConstraint(
            "wordpress_user_id", "idempotency_hash",
            name="uq_certificado_idempotencia",
        ),
        CheckConstraint(
            "status IN ('VALIDO', 'REVOGADO')", name="ck_certificado_status",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(), primary_key=True,
    )
    lote_id: Mapped[int] = mapped_column(
        ForeignKey("lotes.id", ondelete="RESTRICT"), nullable=False,
    )
    snapshot_id: Mapped[int] = mapped_column(
        ForeignKey("snapshots_fechamento.id", ondelete="RESTRICT"),
        nullable=False,
    )
    token_id: Mapped[int] = mapped_column(
        ForeignKey("tokens_publicos.id", ondelete="RESTRICT"),
        nullable=False, unique=True,
    )
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    wordpress_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    idempotency_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    snapshot_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
