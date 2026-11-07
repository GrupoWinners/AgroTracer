from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    Identity,
    Index,
    Integer,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.fator import Fator


class ParametroSet(Base):
    __tablename__ = "parametro_sets"

    __table_args__ = (
        UniqueConstraint(
            "versao",
            name="uq_parametro_sets_versao",
        ),
        CheckConstraint(
            "status IN ('RASCUNHO', 'ATIVO', 'INATIVO')",
            name="ck_parametro_sets_status",
        ),
        CheckConstraint(
            "vigencia_fim IS NULL "
            "OR vigencia_fim >= vigencia_inicio",
            name="ck_parametro_sets_vigencia",
        ),
        CheckConstraint(
            "status <> 'ATIVO' OR "
            "(aprovado_por IS NOT NULL "
            "AND aprovado_em IS NOT NULL)",
            name="ck_parametro_sets_ativo_aprovado",
        ),
        Index(
            "uq_parametro_sets_ativo",
            "status",
            unique=True,
            postgresql_where=text("status = 'ATIVO'"),
            sqlite_where=text("status = 'ATIVO'"),
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(),
        primary_key=True,
        autoincrement=True,
    )

    versao: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="RASCUNHO",
        server_default="RASCUNHO",
    )

    vigencia_inicio: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    vigencia_fim: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    aprovado_por: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    aprovado_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    fatores: Mapped[list["Fator"]] = relationship(
        "Fator",
        back_populates="parametro_set",
    )
