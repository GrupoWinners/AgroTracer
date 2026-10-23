"""Cria produtores, fazendas, talhoes e auditoria_eventos.

Revision ID: s1t01_modelos
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "s1t01_modelos"
down_revision: Union[str, Sequence[str], None] = "4b5cbbc1616c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "produtores",
        sa.Column(
            "id", sa.BigInteger(), sa.Identity(),
            nullable=False,
        ),
        sa.Column(
            "wordpress_user_id", sa.BigInteger(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "wordpress_user_id",
            name="uq_produtores_wordpress_user_id",
        ),
        sa.CheckConstraint(
            "wordpress_user_id > 0",
            name="ck_produtores_wordpress_user_id_positivo",
        ),
    )

    op.create_table(
        "fazendas",
        sa.Column(
            "id", sa.BigInteger(), sa.Identity(),
            nullable=False,
        ),
        sa.Column(
            "produtor_id", sa.BigInteger(),
            nullable=False,
        ),
        sa.Column(
            "numero_car_informado", sa.Text(),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["produtor_id"],
            ["produtores.id"],
            name="fk_fazendas_produtor_id",
            ondelete="RESTRICT",
        ),
    )

    op.create_table(
        "talhoes",
        sa.Column(
            "id", sa.BigInteger(), sa.Identity(),
            nullable=False,
        ),
        sa.Column(
            "fazenda_id", sa.BigInteger(),
            nullable=False,
        ),
        sa.Column(
            "area_hectares", sa.Numeric(12, 4),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["fazenda_id"],
            ["fazendas.id"],
            name="fk_talhoes_fazenda_id",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "area_hectares > 0",
            name="ck_talhoes_area_hectares_positiva",
        ),
    )

    op.create_table(
        "auditoria_eventos",
        sa.Column(
            "id", sa.BigInteger(), sa.Identity(),
            nullable=False,
        ),
        sa.Column(
            "entidade", sa.String(50),
            nullable=False,
        ),
        sa.Column(
            "entidade_id", sa.BigInteger(),
            nullable=True,
        ),
        sa.Column(
            "acao", sa.String(30),
            nullable=False,
        ),
        sa.Column(
            "wordpress_user_id", sa.BigInteger(),
            nullable=True,
        ),
        sa.Column(
            "correlation_id", sa.String(128),
            nullable=True,
        ),
        sa.Column(
            "detalhes", postgresql.JSONB(),
            nullable=True,
        ),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "btrim(acao) <> ''",
            name="ck_auditoria_eventos_acao_obrigatoria",
        ),
        sa.CheckConstraint(
            "btrim(entidade) <> ''",
            name="ck_auditoria_eventos_entidade_obrigatoria",
        ),
    )


def downgrade() -> None:
    op.drop_table("auditoria_eventos")
    op.drop_table("talhoes")
    op.drop_table("fazendas")
    op.drop_table("produtores")
