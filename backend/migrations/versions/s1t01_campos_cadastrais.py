"""Adiciona campos cadastrais e unicidade do CAR.

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
    conexao = op.get_bind()

    # Os novos campos sao obrigatorios.
    # Sem dados cadastrais reais, nao devemos inventar valores
    # para registros que ja existam.
    quantidades = conexao.execute(
        sa.text("""
            SELECT
                (SELECT count(*) FROM fazendas) AS fazendas,
                (SELECT count(*) FROM talhoes) AS talhoes
        """)
    ).one()

    if quantidades.fazendas or quantidades.talhoes:
        raise RuntimeError(
            "Existem fazendas ou talhoes cadastrados. "
            "E necessario planejar o preenchimento dos novos "
            "campos com dados reais antes desta migration."
        )

    op.add_column(
        "fazendas",
        sa.Column("nome", sa.String(120), nullable=False),
    )

    op.add_column(
        "fazendas",
        sa.Column("municipio", sa.String(80), nullable=False),
    )

    op.add_column(
        "fazendas",
        sa.Column("uf", sa.String(2), nullable=False),
    )

    op.create_unique_constraint(
        "uq_fazendas_numero_car_informado",
        "fazendas",
        ["numero_car_informado"],
    )

    op.add_column(
        "talhoes",
        sa.Column(
            "identificador",
            sa.String(50),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("talhoes", "identificador")

    op.drop_constraint(
        "uq_fazendas_numero_car_informado",
        "fazendas",
        type_="unique",
    )

    op.drop_column("fazendas", "uf")
    op.drop_column("fazendas", "municipio")
    op.drop_column("fazendas", "nome")
