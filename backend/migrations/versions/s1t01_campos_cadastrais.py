"""Adiciona campos cadastrais, unicidade do CAR e regras de integridade S1-T01.

Revision ID: s1t01_campos
Revises: s1t01_modelos
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "s1t01_campos"
down_revision: Union[str, Sequence[str], None] = "s1t01_modelos"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Fazendas: adiciona colunas como nullable para permitir backfill seguro em bancos populados
    op.add_column(
        "fazendas",
        sa.Column("nome", sa.String(120), nullable=True),
    )
    op.add_column(
        "fazendas",
        sa.Column("municipio", sa.String(80), nullable=True),
    )
    op.add_column(
        "fazendas",
        sa.Column("uf", sa.String(2), nullable=True),
    )

    # Preenche registros existentes com valores padrao
    op.execute(
        sa.text("""
            UPDATE fazendas
            SET nome = COALESCE(nome, 'Fazenda ' || id),
                municipio = COALESCE(municipio, 'Nao Informado'),
                uf = COALESCE(uf, 'BR')
            WHERE nome IS NULL OR municipio IS NULL OR uf IS NULL
        """)
    )

    # Torna as colunas NOT NULL
    op.alter_column("fazendas", "nome", nullable=False)
    op.alter_column("fazendas", "municipio", nullable=False)
    op.alter_column("fazendas", "uf", nullable=False)

    # Constraints em fazendas
    op.create_unique_constraint(
        "uq_fazendas_numero_car_informado",
        "fazendas",
        ["numero_car_informado"],
    )
    op.create_check_constraint(
        "ck_fazendas_nome_obrigatorio",
        "fazendas",
        "btrim(nome) <> ''",
    )
    op.create_check_constraint(
        "ck_fazendas_municipio_obrigatorio",
        "fazendas",
        "btrim(municipio) <> ''",
    )
    op.create_check_constraint(
        "ck_fazendas_uf_tamanho",
        "fazendas",
        "char_length(uf) = 2",
    )

    # 2. Talhoes: adiciona identificador com backfill seguro
    op.add_column(
        "talhoes",
        sa.Column(
            "identificador",
            sa.String(50),
            nullable=True,
        ),
    )
    op.execute(
        sa.text("""
            UPDATE talhoes
            SET identificador = COALESCE(identificador, 'Talhao ' || id)
            WHERE identificador IS NULL
        """)
    )
    op.alter_column("talhoes", "identificador", nullable=False)

    # Constraints em talhoes
    op.create_check_constraint(
        "ck_talhoes_identificador_obrigatorio",
        "talhoes",
        "btrim(identificador) <> ''",
    )
    op.create_unique_constraint(
        "uq_talhoes_fazenda_identificador",
        "talhoes",
        ["fazenda_id", "identificador"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_talhoes_fazenda_identificador",
        "talhoes",
        type_="unique",
    )
    op.drop_constraint(
        "ck_talhoes_identificador_obrigatorio",
        "talhoes",
        type_="check",
    )
    op.drop_column("talhoes", "identificador")

    op.drop_constraint(
        "ck_fazendas_uf_tamanho",
        "fazendas",
        type_="check",
    )
    op.drop_constraint(
        "ck_fazendas_municipio_obrigatorio",
        "fazendas",
        type_="check",
    )
    op.drop_constraint(
        "ck_fazendas_nome_obrigatorio",
        "fazendas",
        type_="check",
    )
    op.drop_constraint(
        "uq_fazendas_numero_car_informado",
        "fazendas",
        type_="unique",
    )
    op.drop_column("fazendas", "uf")
    op.drop_column("fazendas", "municipio")
    op.drop_column("fazendas", "nome")
