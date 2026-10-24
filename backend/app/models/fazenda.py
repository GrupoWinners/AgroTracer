from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Identity,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.produtor import Produtor
    from app.models.talhao import Talhao


class Fazenda(Base):
    __tablename__ = "fazendas"

    __table_args__ = (
        UniqueConstraint(
            "numero_car_informado",
            name="uq_fazendas_numero_car_informado",
        ),
        CheckConstraint(
            "btrim(nome) <> ''",
            name="ck_fazendas_nome_obrigatorio",
        ),
        CheckConstraint(
            "btrim(municipio) <> ''",
            name="ck_fazendas_municipio_obrigatorio",
        ),
        CheckConstraint(
            "char_length(uf) = 2",
            name="ck_fazendas_uf_tamanho",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(),
        primary_key=True,
        autoincrement=True,
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

    produtor: Mapped["Produtor"] = relationship(
        "Produtor",
        back_populates="fazendas",
    )

    talhoes: Mapped[list["Talhao"]] = relationship(
        "Talhao",
        back_populates="fazenda",
    )
