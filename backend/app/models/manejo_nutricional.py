"""S3-T01: modelo de manejo nutricional."""

from datetime import date

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    ForeignKey,
    Identity,
    Integer,
    String,
    column,
    func,
    literal_column,
)
from sqlalchemy.dialects.postgresql import ExcludeConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ManejoNutricional(Base):
    __tablename__ = "manejos_nutricionais"

    __table_args__ = (
        CheckConstraint(
            "fim >= inicio",
            name="ck_manejos_nutricionais_datas",
        ),
        CheckConstraint(
            "btrim(tipo_dieta) <> ''",
            name="ck_manejos_nutricionais_tipo_dieta",
        ),
        ExcludeConstraint(
            ("lote_id", "="),
            (
                func.daterange(
                    column("inicio"),
                    column("fim"),
                    literal_column("'[]'"),
                ),
                "&&",
            ),
            using="gist",
            name="ex_manejos_nutricionais_periodo",
        ).ddl_if(dialect="postgresql"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(),
        primary_key=True,
    )

    lote_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("lotes.id", ondelete="RESTRICT"),
        nullable=False,
    )

    inicio: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    fim: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    parametro_set_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "parametro_sets.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    tipo_dieta: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
