"""habilita extensao btree_gist

Revision ID: 4b5cbbc1616c
Revises:
Create Date: 2026-10-19 16:13:27.723870

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b5cbbc1616c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "CREATE EXTENSION IF NOT EXISTS btree_gist"
    )


def downgrade() -> None:
    pass
