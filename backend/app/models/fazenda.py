from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Identity,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Fazenda(Base):
    __tablename__ = "fazendas"

    __table_args__ = (
        UniqueConstraint(
            "numero_car_informado",
            name="uq_fazendas_numero_car_informado",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True,
    )

    produtor_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "produtores.id",
            name="fk_fazendas_produtor_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    nome: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    municipio: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    uf: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
    )

    numero_car_informado: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
