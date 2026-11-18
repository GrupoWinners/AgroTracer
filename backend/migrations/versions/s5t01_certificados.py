"""S5-T01: certificado valido unico e idempotencia por usuario."""

from alembic import op
import sqlalchemy as sa

revision = "s5t01_certificados"
down_revision = "s5t03_tokens"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "certificados",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("lote_id", sa.BigInteger(), nullable=False),
        sa.Column("snapshot_id", sa.BigInteger(), nullable=False),
        sa.Column("token_id", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("wordpress_user_id", sa.BigInteger(), nullable=False),
        sa.Column("idempotency_hash", sa.String(64), nullable=False),
        sa.Column("request_hash", sa.String(64), nullable=False),
        sa.Column("snapshot_sha256", sa.String(64), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["lote_id"], ["lotes.id"],
                                ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["snapshot_id"], ["snapshots_fechamento.id"],
                                ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["token_id"], ["tokens_publicos.id"],
                                ondelete="RESTRICT"),
        sa.UniqueConstraint("token_id", name="uq_certificado_token"),
        sa.UniqueConstraint("wordpress_user_id", "idempotency_hash",
                            name="uq_certificado_idempotencia"),
        sa.CheckConstraint("status IN ('VALIDO', 'REVOGADO')",
                           name="ck_certificado_status"),
    )
    op.create_index(
        "uq_certificado_valido_por_lote", "certificados", ["lote_id"],
        unique=True, postgresql_where=sa.text("status = 'VALIDO'"),
    )


def downgrade():
    op.drop_table("certificados")
