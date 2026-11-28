"""Somente o digest do token publico e persistido."""

from sqlalchemy import BigInteger, Identity, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TokenPublico(Base):
    __tablename__ = "tokens_publicos"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(), primary_key=True,
    )
    token_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True,
    )
