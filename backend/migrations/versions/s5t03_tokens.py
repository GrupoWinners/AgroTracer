"""S5-T03: token publico persistido exclusivamente como hash."""

from alembic import op
import sqlalchemy as sa

revision = "s5t03_tokens"
down_revision = "s4t03_snapshots"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tokens_publicos",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.UniqueConstraint("token_hash", name="uq_tokens_publicos_hash"),
    )


def downgrade():
    op.drop_table("tokens_publicos")
