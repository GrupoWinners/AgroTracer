"""S5-T02: arquivo e hash persistidos depois da geracao."""

from alembic import op
import sqlalchemy as sa

revision = "s5t02_pdf"
down_revision = "s5t01_certificados"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "certificados_pdf",
        sa.Column("certificado_id", sa.BigInteger(), primary_key=True),
        sa.Column("conteudo", sa.LargeBinary(), nullable=False),
        sa.Column("pdf_sha256", sa.String(64), nullable=False),
        sa.ForeignKeyConstraint(["certificado_id"], ["certificados.id"],
                                ondelete="RESTRICT"),
    )


def downgrade():
    op.drop_table("certificados_pdf")
