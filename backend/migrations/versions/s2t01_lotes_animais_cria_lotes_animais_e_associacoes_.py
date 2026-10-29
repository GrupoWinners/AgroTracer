"""Cria lotes, animais e associacoes temporais.

Revision ID: s2t01_lotes_animais
Revises: s1t01_campos
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "s2t01_lotes_animais"
down_revision: Union[str, Sequence[str], None] = "s1t01_campos"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # RN-04: lote pertence a uma fazenda.
    op.create_table(
        "lotes",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(),
            nullable=False,
        ),
        sa.Column(
            "fazenda_id",
            sa.BigInteger(),
            nullable=False,
        ),
        sa.Column(
            "codigo_lote",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["fazenda_id"],
            ["fazendas.id"],
            name="fk_lotes_fazenda_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "codigo_lote",
            name="uq_lotes_codigo_lote",
        ),
    )

    # RN-05: identificador unico; RFID opcional.
    # ADR-003: animais nao possui lote_id.
    op.create_table(
        "animais",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(),
            nullable=False,
        ),
        sa.Column(
            "produtor_id",
            sa.BigInteger(),
            nullable=False,
        ),
        sa.Column(
            "identificador",
            sa.String(length=80),
            nullable=False,
        ),
        sa.Column(
            "rfid",
            sa.String(length=80),
            nullable=True,
        ),
        sa.Column(
            "data_nascimento_estimada",
            sa.Date(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["produtor_id"],
            ["produtores.id"],
            name="fk_animais_produtor_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "identificador",
            name="uq_animais_identificador",
        ),
    )

    # ADR-003: historico temporal de associacoes.
    op.create_table(
        "lote_animais",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(),
            nullable=False,
        ),
        sa.Column(
            "animal_id",
            sa.BigInteger(),
            nullable=False,
        ),
        sa.Column(
            "lote_id",
            sa.BigInteger(),
            nullable=False,
        ),
        sa.Column(
            "associado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "desassociado_em",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.CheckConstraint(
            "desassociado_em IS NULL "
            "OR desassociado_em >= associado_em",
            name="ck_lote_animais_periodo_valido",
        ),
        sa.ForeignKeyConstraint(
            ["animal_id"],
            ["animais.id"],
            name="fk_lote_animais_animal_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["lote_id"],
            ["lotes.id"],
            name="fk_lote_animais_lote_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # RN-06: um animal so pode ter uma associacao ativa.
    op.create_index(
        "uq_animal_associacao_ativa",
        "lote_animais",
        ["animal_id"],
        unique=True,
        postgresql_where=sa.text(
            "desassociado_em IS NULL"
        ),
    )


def downgrade() -> None:
    # Remover primeiro os objetos que dependem de outros.
    op.drop_index(
        "uq_animal_associacao_ativa",
        table_name="lote_animais",
    )

    op.drop_table("lote_animais")
    op.drop_table("animais")
    op.drop_table("lotes")
