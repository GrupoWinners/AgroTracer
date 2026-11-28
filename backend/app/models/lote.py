from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Identity,
    String,
    UniqueConstraint,
    Integer,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.fazenda import Fazenda
    from app.models.lote_animal import LoteAnimal


class Lote(Base):
    __tablename__ = "lotes"

    __table_args__ = (
        UniqueConstraint(
            "codigo_lote",
            name="uq_lotes_codigo_lote",
        ),
        CheckConstraint(
            "status IN ('RASCUNHO', 'EM_MANEJO', 'FECHADO')",
            name="ck_lotes_status_valido",
        ),
    )
    fazenda: Mapped["Fazenda"] = relationship(
        "Fazenda",
        back_populates="lotes",
    )
    associacoes_animais: Mapped[list["LoteAnimal"]] = relationship(
        "LoteAnimal",
        back_populates="lote",
    )

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(),
        primary_key=True,
        autoincrement=True,
    )

    fazenda_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "fazendas.id",
            name="fk_lotes_fazenda_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    codigo_lote: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
