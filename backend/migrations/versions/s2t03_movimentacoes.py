"""S2-T03: cria movimentacoes com XOR e FKs RESTRICT."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "s2t03_movimentacoes"
down_revision: Union[str, None] = "s2t01_estados"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "movimentacoes",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(),
            primary_key=True,
        ),
        sa.Column("animal_id", sa.BigInteger(), nullable=True),
        sa.Column("lote_id", sa.BigInteger(), nullable=True),
        sa.Column(
            "origem_talhao_id",
            sa.BigInteger(),
            nullable=True,
        ),
        sa.Column(
            "destino_talhao_id",
            sa.BigInteger(),
            nullable=True,
        ),
        sa.Column("tipo", sa.String(30), nullable=False),
        sa.Column(
            "data_hora",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "observacao",
            sa.String(500),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["animal_id"],
            ["animais.id"],
            name="fk_movimentacoes_animal_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["lote_id"],
            ["lotes.id"],
            name="fk_movimentacoes_lote_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["origem_talhao_id"],
            ["talhoes.id"],
            name="fk_movimentacoes_origem_talhao_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["destino_talhao_id"],
            ["talhoes.id"],
            name="fk_movimentacoes_destino_talhao_id",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "(animal_id IS NOT NULL) <> (lote_id IS NOT NULL)",
            name="ck_movimentacoes_alvo_xor",
        ),
        sa.CheckConstraint(
            "origem_talhao_id IS NULL "
            "OR destino_talhao_id IS NULL "
            "OR origem_talhao_id <> destino_talhao_id",
            name="ck_movimentacoes_origem_destino",
        ),
    )


def downgrade() -> None:
    op.drop_table("movimentacoes")
