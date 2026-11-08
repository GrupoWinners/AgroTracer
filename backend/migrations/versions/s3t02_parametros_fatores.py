"""S3-T02: conjuntos de parametros e fatores versionados."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "s3t02_parametros"
down_revision: Union[str, None] = "s2t03_movimentacoes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "parametro_sets",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(),
            primary_key=True,
        ),
        sa.Column(
            "versao",
            sa.String(80),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="RASCUNHO",
        ),
        sa.Column(
            "vigencia_inicio",
            sa.Date(),
            nullable=False,
        ),
        sa.Column(
            "vigencia_fim",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "aprovado_por",
            sa.String(120),
            nullable=True,
        ),
        sa.Column(
            "aprovado_em",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.UniqueConstraint(
            "versao",
            name="uq_parametro_sets_versao",
        ),
        sa.CheckConstraint(
            "status IN ('RASCUNHO', 'ATIVO', 'INATIVO')",
            name="ck_parametro_sets_status",
        ),
        sa.CheckConstraint(
            "vigencia_fim IS NULL "
            "OR vigencia_fim >= vigencia_inicio",
            name="ck_parametro_sets_vigencia",
        ),
        sa.CheckConstraint(
            "status <> 'ATIVO' OR "
            "(aprovado_por IS NOT NULL "
            "AND aprovado_em IS NOT NULL)",
            name="ck_parametro_sets_ativo_aprovado",
        ),
    )

    # Somente um conjunto ativo por vez.
    # O indice parcial tambem protege contra concorrencia.
    op.create_index(
        "uq_parametro_sets_ativo",
        "parametro_sets",
        ["status"],
        unique=True,
        postgresql_where=sa.text("status = 'ATIVO'"),
    )

    op.create_table(
        "fatores",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(),
            primary_key=True,
        ),
        sa.Column(
            "parametro_set_id",
            sa.BigInteger(),
            nullable=False,
        ),
        sa.Column(
            "chave",
            sa.String(100),
            nullable=False,
        ),
        sa.Column(
            "unidade",
            sa.String(100),
            nullable=False,
        ),
        sa.Column(
            "valor",
            sa.Numeric(24, 12),
            nullable=False,
        ),
        sa.Column(
            "source_type",
            sa.String(30),
            nullable=False,
        ),
        sa.Column(
            "source_uri",
            sa.String(500),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["parametro_set_id"],
            ["parametro_sets.id"],
            name="fk_fatores_parametro_set_id",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "parametro_set_id",
            "chave",
            name="uq_fatores_set_chave",
        ),
        sa.CheckConstraint(
            "source_type IN ("
            "'SYNTHETIC', 'PROFESSOR_APPROVED', "
            "'IPCC', 'EMBRAPA', 'OTHER')",
            name="ck_fatores_source_type",
        ),
        sa.CheckConstraint(
            "source_type = 'SYNTHETIC' OR "
            "(source_uri IS NOT NULL "
            "AND trim(source_uri) <> '')",
            name="ck_fatores_source_uri",
        ),
        sa.CheckConstraint(
            "trim(chave) <> ''",
            name="ck_fatores_chave",
        ),
        sa.CheckConstraint(
            "trim(unidade) <> ''",
            name="ck_fatores_unidade",
        ),
    )


def downgrade() -> None:
    op.drop_table("fatores")

    op.drop_index(
        "uq_parametro_sets_ativo",
        table_name="parametro_sets",
    )

    op.drop_table("parametro_sets")
