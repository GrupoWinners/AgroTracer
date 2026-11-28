"""S3-T02: protege historico de parametros e fatores."""

from typing import Sequence, Union

from alembic import op


revision: str = "s3t02_historico"
down_revision: Union[str, None] = "s3t02_parametros"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Uma versao publicada nao pode ser editada ou excluida.
    # A unica transicao permitida apos publicacao e
    # ATIVO -> INATIVO, preservando todos os outros campos.
    op.execute("""
        CREATE FUNCTION proteger_parametro_set()
        RETURNS trigger AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                IF NEW.status <> 'RASCUNHO' THEN
                    RAISE EXCEPTION
                        'Novo conjunto deve iniciar em RASCUNHO';
                END IF;
                RETURN NEW;
            END IF;

            IF TG_OP = 'DELETE' THEN
                IF OLD.status <> 'RASCUNHO' THEN
                    RAISE EXCEPTION
                        'Versao publicada nao pode ser excluida';
                END IF;
                RETURN OLD;
            END IF;

            IF NEW.id <> OLD.id THEN
                RAISE EXCEPTION
                    'ID do conjunto nao pode ser alterado';
            END IF;

            IF OLD.status = 'RASCUNHO' THEN
                IF NEW.status NOT IN ('RASCUNHO', 'ATIVO') THEN
                    RAISE EXCEPTION
                        'Transicao de status invalida';
                END IF;
                RETURN NEW;
            END IF;

            IF OLD.status = 'ATIVO'
               AND NEW.status = 'INATIVO'
               AND (to_jsonb(NEW) - 'status')
                   = (to_jsonb(OLD) - 'status') THEN
                RETURN NEW;
            END IF;

            RAISE EXCEPTION
                'Versao publicada e imutavel';
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER trg_proteger_parametro_set
        BEFORE INSERT OR UPDATE OR DELETE
        ON parametro_sets
        FOR EACH ROW
        EXECUTE FUNCTION proteger_parametro_set();
    """)

    # Fatores somente podem ser editados no RASCUNHO.
    # O lock no conjunto evita conflito com ativacao
    # simultanea em outra transacao.
    op.execute("""
        CREATE FUNCTION proteger_fator_historico()
        RETURNS trigger AS $$
        DECLARE
            conjunto_id BIGINT;
            estado VARCHAR(20);
        BEGIN
            IF TG_OP = 'INSERT' THEN
                conjunto_id := NEW.parametro_set_id;
            ELSE
                conjunto_id := OLD.parametro_set_id;
            END IF;

            SELECT status INTO estado
            FROM parametro_sets
            WHERE id = conjunto_id
            FOR UPDATE;

            IF estado IS NOT NULL
               AND estado <> 'RASCUNHO' THEN
                RAISE EXCEPTION
                    'Fator de versao publicada e imutavel';
            END IF;

            IF TG_OP = 'UPDATE' THEN
                IF NEW.parametro_set_id
                   <> OLD.parametro_set_id THEN
                    RAISE EXCEPTION
                        'Fator nao pode mudar de conjunto';
                END IF;
            END IF;

            IF TG_OP = 'DELETE' THEN
                RETURN OLD;
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER trg_proteger_fator_historico
        BEFORE INSERT OR UPDATE OR DELETE
        ON fatores
        FOR EACH ROW
        EXECUTE FUNCTION proteger_fator_historico();
    """)


def downgrade() -> None:
    op.execute("""
        DROP TRIGGER trg_proteger_fator_historico
        ON fatores;
    """)
    op.execute("DROP FUNCTION proteger_fator_historico();")

    op.execute("""
        DROP TRIGGER trg_proteger_parametro_set
        ON parametro_sets;
    """)
    op.execute("DROP FUNCTION proteger_parametro_set();")
