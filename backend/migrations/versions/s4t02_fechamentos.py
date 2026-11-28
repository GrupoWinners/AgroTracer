"""S4-T02: persistencia de fechamento e resultados de lote."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "s4t02_fechamentos"
down_revision: Union[str, None] = "s3t01_manejos"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "fechamentos_lote",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("lote_id", sa.BigInteger(), nullable=False),
        sa.Column("parametro_set_id", sa.BigInteger(), nullable=False),
        sa.Column("versao_metodo", sa.String(80), nullable=False),
        sa.Column("data_abate", sa.Date(), nullable=False),
        sa.Column("numero_animais_abate", sa.Integer(), nullable=False),
        sa.Column("peso_medio_abate_kg", sa.Numeric(24, 12), nullable=False),
        sa.Column("rendimento_carcaca", sa.Numeric(24, 12), nullable=False),
        sa.Column("emissao_total_kg_co2e", sa.Numeric(38, 18),
                  nullable=False),
        sa.Column("intensidade_kg_co2e_kg", sa.Numeric(38, 18),
                  nullable=False),
        sa.ForeignKeyConstraint(
            ["lote_id"], ["lotes.id"],
            name="fk_fechamentos_lote_lote", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["parametro_set_id"], ["parametro_sets.id"],
            name="fk_fechamentos_parametro_set", ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("lote_id", name="uq_fechamentos_lote"),
        sa.CheckConstraint(
            "numero_animais_abate > 0",
            name="ck_fechamento_animais_positivos",
        ),
        sa.CheckConstraint(
            "peso_medio_abate_kg > 0",
            name="ck_fechamento_peso_positivo",
        ),
        sa.CheckConstraint(
            "rendimento_carcaca > 0 AND rendimento_carcaca <= 1",
            name="ck_fechamento_rendimento",
        ),
        sa.CheckConstraint(
            "emissao_total_kg_co2e >= 0 AND intensidade_kg_co2e_kg >= 0",
            name="ck_fechamento_resultados",
        ),
    )


def downgrade() -> None:
    op.drop_table("fechamentos_lote")
