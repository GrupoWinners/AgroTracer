from sqlalchemy import BigInteger, ForeignKey, Identity, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Fazenda(Base):
    __tablename__ = "fazendas"

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

    numero_car_informado: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
