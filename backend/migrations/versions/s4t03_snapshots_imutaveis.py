"""S4-T03: snapshot imutavel e fechamento atomicamente vinculado."""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from alembic import op


revision: str = "s4t03_snapshots"
down_revision: Union[str, None] = "s4t02_fechamentos"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "snapshots_fechamento",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("fechamento_id", sa.BigInteger(), nullable=False),
        sa.Column("lote_id", sa.BigInteger(), nullable=False),
        sa.Column("parametro_set_id", sa.BigInteger(), nullable=False),
        sa.Column("versao_parametros", sa.String(80), nullable=False),
        sa.Column("versao_metodo", sa.String(80), nullable=False),
        sa.Column("entradas", JSONB(), nullable=False),
        sa.Column("resultados", JSONB(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["fechamento_id"], ["fechamentos_lote.id"],
            name="fk_snapshots_fechamento", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["lote_id"], ["lotes.id"],
            name="fk_snapshots_lote", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["parametro_set_id"], ["parametro_sets.id"],
            name="fk_snapshots_parametro_set", ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "fechamento_id", name="uq_snapshots_fechamento",
        ),
    )
    op.execute("""
        CREATE FUNCTION bloquear_mutacao_snapshot()
        RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION
                'Snapshot publicado nao pode ser editado ou excluido';
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER trg_snapshot_imutavel
        BEFORE UPDATE OR DELETE ON snapshots_fechamento
        FOR EACH ROW EXECUTE FUNCTION bloquear_mutacao_snapshot();
    """)
    # Um fechamento nao pode ser confirmado sem o seu snapshot.
    # Trigger adiado permite inserir fechamento e snapshot na
    # mesma transacao antes do COMMIT.
    op.execute("""
        CREATE FUNCTION exigir_snapshot_no_fechamento()
        RETURNS trigger AS $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM snapshots_fechamento
                WHERE fechamento_id = NEW.id
                  AND lote_id = NEW.lote_id
                  AND parametro_set_id = NEW.parametro_set_id
                  AND versao_metodo = NEW.versao_metodo
            ) THEN
                RAISE EXCEPTION
                    'Fechamento exige snapshot consistente';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE CONSTRAINT TRIGGER trg_fechamento_snapshot
        AFTER INSERT ON fechamentos_lote
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION exigir_snapshot_no_fechamento();
    """)


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER trg_fechamento_snapshot ON fechamentos_lote;"
    )
    op.execute("DROP FUNCTION exigir_snapshot_no_fechamento();")
    op.execute(
        "DROP TRIGGER trg_snapshot_imutavel ON snapshots_fechamento;"
    )
    op.execute("DROP FUNCTION bloquear_mutacao_snapshot();")
    op.drop_table("snapshots_fechamento")
