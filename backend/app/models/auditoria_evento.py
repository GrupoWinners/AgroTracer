from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Identity,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AuditoriaEvento(Base):
    __tablename__ = "auditoria_eventos"

    __table_args__ = (
        CheckConstraint(
            "btrim(acao) <> ''",
            name="ck_auditoria_eventos_acao_obrigatoria",
        ),
        CheckConstraint(
            "btrim(entidade) <> ''",
            name="ck_auditoria_eventos_entidade_obrigatoria",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(),
        primary_key=True,
        autoincrement=True,
    )

    entidade: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    entidade_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    acao: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    wordpress_user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    correlation_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    detalhes: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
