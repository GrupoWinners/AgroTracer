from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Identity,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.fazenda import Fazenda
    from app.models.animal import Animal


class Produtor(Base):
    __tablename__ = "produtores"

    __table_args__ = (
        UniqueConstraint(
            "wordpress_user_id",
            name="uq_produtores_wordpress_user_id",
        ),
        CheckConstraint(
            "wordpress_user_id > 0",
            name="ck_produtores_wordpress_user_id_positivo",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(),
        primary_key=True,
        autoincrement=True,
    )

    wordpress_user_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    fazendas: Mapped[list["Fazenda"]] = relationship(
        "Fazenda",
        back_populates="produtor",
    )

    animais: Mapped[list["Animal"]] = relationship(
        "Animal",
        back_populates="produtor",
    )
