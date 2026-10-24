from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Identity,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.fazenda import Fazenda


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
        BigInteger,
        Identity(),
        primary_key=True,
    )

    wordpress_user_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    fazendas: Mapped[list["Fazenda"]] = relationship(
        "Fazenda",
        back_populates="produtor",
    )
