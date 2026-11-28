"""Restringe os estados permitidos dos lotes na S2-T01.

Revision ID: s2t01_estados
Revises: s2t01_lotes_animais
"""

from alembic import op


revision = "s2t01_estados"
down_revision = "s2t01_lotes_animais"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_lotes_status_valido",
        "lotes",
        "status IN ('RASCUNHO', 'EM_MANEJO', 'FECHADO')",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_lotes_status_valido",
        "lotes",
        type_="check",
    )
