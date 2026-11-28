"""S3-T02: ativacao auditada de parametros versionados."""

from datetime import datetime, timezone

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.models.fator import Fator
from app.models.parametro_set import ParametroSet
from app.services.audit_service import registrar_auditoria


class ErroParametro(Exception):
    def __init__(
        self,
        status_code: int,
        codigo: str,
        mensagem: str,
    ):
        self.status_code = status_code
        self.codigo = codigo
        self.mensagem = mensagem
        super().__init__(mensagem)


def ativar_parametro_set(
    db: Session,
    parametro_set_id: int,
    wordpress_user_id: int,
    justificativa: str,
    correlation_id: str | None = None,
) -> ParametroSet:
    """Ativa uma versao e audita toda a transicao.

    O chamador deve:
    - verificar permissao administrativa;
    - confirmar a transacao com commit;
    - executar rollback em caso de erro.

    Usa lock transacional para serializar ativacoes.
    """

    justificativa = justificativa.strip()

    if not justificativa or len(justificativa) > 500:
        raise ErroParametro(
            422,
            "JUSTIFICATIVA_INVALIDA",
            "Informe justificativa de 1 a 500 caracteres.",
        )

    if wordpress_user_id <= 0:
        raise ErroParametro(
            403,
            "ADMIN_REQUIRED",
            "A operacao exige administrador autenticado.",
        )

    # Serializa as ativacoes mesmo quando sao
    # realizadas sobre conjuntos diferentes.
    # O lock e liberado no COMMIT ou ROLLBACK.
    db.execute(
        text("SELECT pg_advisory_xact_lock(43829, 1)")
    )

    conjunto = db.scalar(
        select(ParametroSet)
        .where(ParametroSet.id == parametro_set_id)
        .with_for_update()
    )

    if conjunto is None:
        raise ErroParametro(
            404,
            "PARAMETRO_SET_NAO_ENCONTRADO",
            "Conjunto de parametros nao encontrado.",
        )

    if conjunto.status == "ATIVO":
        raise ErroParametro(
            409,
            "PARAMETRO_SET_JA_ATIVO",
            "Este conjunto ja esta ativo.",
        )

    if conjunto.status != "RASCUNHO":
        raise ErroParametro(
            409,
            "PARAMETRO_SET_IMUTAVEL",
            "Versao historica nao pode ser reativada.",
        )

    fator_id = db.scalar(
        select(Fator.id)
        .where(Fator.parametro_set_id == conjunto.id)
        .limit(1)
    )

    if fator_id is None:
        raise ErroParametro(
            422,
            "PARAMETRO_SET_SEM_FATORES",
            "Cadastre ao menos um fator antes da ativacao.",
        )

    atual = db.scalar(
        select(ParametroSet)
        .where(ParametroSet.status == "ATIVO")
        .with_for_update()
    )

    anterior_id = None

    if atual is not None:
        anterior_id = atual.id
        atual.status = "INATIVO"

        registrar_auditoria(
            db=db,
            entidade="parametro_set",
            entidade_id=atual.id,
            acao="INATIVAR",
            wordpress_user_id=wordpress_user_id,
            correlation_id=correlation_id,
            detalhes={
                "justificativa": justificativa,
                "substituido_por_id": conjunto.id,
            },
        )

        # Libera o indice UNIQUE parcial antes
        # de ativar a nova versao.
        db.flush()

    conjunto.status = "ATIVO"
    conjunto.aprovado_por = f"wp:{wordpress_user_id}"
    conjunto.aprovado_em = datetime.now(timezone.utc)

    registrar_auditoria(
        db=db,
        entidade="parametro_set",
        entidade_id=conjunto.id,
        acao="ATIVAR",
        wordpress_user_id=wordpress_user_id,
        correlation_id=correlation_id,
        detalhes={
            "justificativa": justificativa,
            "versao": conjunto.versao,
            "versao_anterior_id": anterior_id,
        },
    )

    db.flush()
    return conjunto
