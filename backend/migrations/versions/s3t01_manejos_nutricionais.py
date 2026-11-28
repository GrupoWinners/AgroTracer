"""S3-T01: manejo nutricional com EXCLUDE GiST."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "s3t01_manejos"
down_revision: Union[str, None] = "s3t02_historico"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Necessaria para igualdade de BIGINT em GiST.
    op.execute(
        "CREATE EXTENSION IF NOT EXISTS btree_gist"
    )

    op.create_table(
        "manejos_nutricionais",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(),
            primary_key=True,
        ),
        sa.Column(
            "lote_id",
            sa.BigInteger(),
            nullable=False,
        ),
        sa.Column(
            "inicio",
            sa.Date(),
            nullable=False,
        ),
        sa.Column(
            "fim",
            sa.Date(),
            nullable=False,
        ),
        sa.Column(
            "parametro_set_id",
            sa.BigInteger(),
            nullable=False,
        ),
        sa.Column(
            "tipo_dieta",
            sa.String(50),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["lote_id"],
            ["lotes.id"],
            name="fk_manejos_nutricionais_lote",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["parametro_set_id"],
            ["parametro_sets.id"],
            name="fk_manejos_nutricionais_parametro_set",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "fim >= inicio",
            name="ck_manejos_nutricionais_datas",
        ),
        sa.CheckConstraint(
            "btrim(tipo_dieta) <> ''",
            name="ck_manejos_nutricionais_tipo_dieta",
        ),
    )

    op.create_exclude_constraint(
        "ex_manejos_nutricionais_periodo",
        "manejos_nutricionais",
        ("lote_id", "="),
        (
            sa.func.daterange(
                sa.column("inicio"),
                sa.column("fim"),
                sa.literal_column("'[]'"),
            ),
            "&&",
        ),
        using="gist",
    )


def downgrade() -> None:
    op.drop_table("manejos_nutricionais")
