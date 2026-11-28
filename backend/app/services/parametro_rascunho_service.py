"""S3-T02: edicao auditada de parametros em rascunho."""

from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.fator import Fator
from app.models.parametro_set import ParametroSet
from app.services.audit_service import registrar_auditoria
from app.services.parametro_service import ErroParametro


FONTES = {
    "SYNTHETIC",
    "PROFESSOR_APPROVED",
    "IPCC",
    "EMBRAPA",
    "OTHER",
}


def _validar_ator_e_justificativa(
    wordpress_user_id: int,
    justificativa: str,
) -> str:
    if wordpress_user_id <= 0:
        raise ErroParametro(
            403,
            "ADMIN_REQUIRED",
            "Administrador autenticado obrigatorio.",
        )

    razao = justificativa.strip()
    if not 1 <= len(razao) <= 500:
        raise ErroParametro(
            422,
            "JUSTIFICATIVA_INVALIDA",
            "Informe uma justificativa de 1 a 500 caracteres.",
        )
    return razao


def _obter_rascunho(db: Session, conjunto_id: int):
    conjunto = db.scalar(
        select(ParametroSet)
        .where(ParametroSet.id == conjunto_id)
        .with_for_update()
    )

    if conjunto is None:
        raise ErroParametro(
            404,
            "PARAMETRO_SET_NAO_ENCONTRADO",
            "Conjunto de parametros nao encontrado.",
        )

    if conjunto.status != "RASCUNHO":
        raise ErroParametro(
            409,
            "PARAMETRO_SET_IMUTAVEL",
            "Somente rascunhos podem ser alterados.",
        )

    return conjunto


def _validar_campos_fator(
    chave: str,
    unidade: str,
    valor: Decimal,
    source_type: str,
    source_uri: str | None,
):
    chave = chave.strip()
    unidade = unidade.strip()
    uri = source_uri.strip() if source_uri else None

    if not 1 <= len(chave) <= 100:
        raise ErroParametro(
            422, "CHAVE_INVALIDA", "Chave de fator invalida."
        )

    if not 1 <= len(unidade) <= 100:
        raise ErroParametro(
            422, "UNIDADE_INVALIDA", "Unidade invalida."
        )

    if not isinstance(valor, Decimal) or not valor.is_finite():
        raise ErroParametro(
            422,
            "VALOR_INVALIDO",
            "Informe um valor Decimal finito.",
        )

    if source_type not in FONTES:
        raise ErroParametro(
            422,
            "SOURCE_TYPE_INVALIDO",
            "Classificacao da fonte invalida.",
        )

    if source_type != "SYNTHETIC" and not uri:
        raise ErroParametro(
            422,
            "FONTE_OBRIGATORIA",
            "Informe a referencia da fonte nao sintetica.",
        )

    if uri is not None and len(uri) > 500:
        raise ErroParametro(
            422,
            "SOURCE_URI_INVALIDA",
            "Referencia deve ter ate 500 caracteres.",
        )

    return chave, unidade, uri


def criar_fator_rascunho(
    db: Session,
    parametro_set_id: int,
    chave: str,
    unidade: str,
    valor: Decimal,
    source_type: str,
    source_uri: str | None,
    wordpress_user_id: int,
    justificativa: str,
    correlation_id: str | None = None,
) -> Fator:
    razao = _validar_ator_e_justificativa(
        wordpress_user_id, justificativa
    )
    _obter_rascunho(db, parametro_set_id)

    chave, unidade, uri = _validar_campos_fator(
        chave, unidade, valor, source_type, source_uri
    )

    fator = Fator(
        parametro_set_id=parametro_set_id,
        chave=chave,
        unidade=unidade,
        valor=valor,
        source_type=source_type,
        source_uri=uri,
    )
    db.add(fator)
    db.flush()

    registrar_auditoria(
        db=db,
        entidade="fator",
        entidade_id=fator.id,
        acao="CRIAR",
        wordpress_user_id=wordpress_user_id,
        correlation_id=correlation_id,
        detalhes={
            "parametro_set_id": parametro_set_id,
            "chave": chave,
            "unidade": unidade,
            "valor": str(valor),
            "source_type": source_type,
            "source_uri": uri,
            "justificativa": razao,
        },
    )
    return fator


def atualizar_fator_rascunho(
    db: Session,
    parametro_set_id: int,
    fator_id: int,
    chave: str,
    unidade: str,
    valor: Decimal,
    source_type: str,
    source_uri: str | None,
    wordpress_user_id: int,
    justificativa: str,
    correlation_id: str | None = None,
) -> Fator:
    razao = _validar_ator_e_justificativa(
        wordpress_user_id, justificativa
    )
    _obter_rascunho(db, parametro_set_id)

    fator = db.scalar(
        select(Fator)
        .where(
            Fator.id == fator_id,
            Fator.parametro_set_id == parametro_set_id,
        )
        .with_for_update()
    )

    if fator is None:
        raise ErroParametro(
            404, "FATOR_NAO_ENCONTRADO", "Fator nao encontrado."
        )

    chave, unidade, uri = _validar_campos_fator(
        chave, unidade, valor, source_type, source_uri
    )

    anterior = {
        "chave": fator.chave,
        "unidade": fator.unidade,
        "valor": str(fator.valor),
        "source_type": fator.source_type,
        "source_uri": fator.source_uri,
    }

    fator.chave = chave
    fator.unidade = unidade
    fator.valor = valor
    fator.source_type = source_type
    fator.source_uri = uri

    db.flush()

    registrar_auditoria(
        db=db,
        entidade="fator",
        entidade_id=fator.id,
        acao="ATUALIZAR",
        wordpress_user_id=wordpress_user_id,
        correlation_id=correlation_id,
        detalhes={
            "parametro_set_id": parametro_set_id,
            "antes": anterior,
            "depois": {
                "chave": chave,
                "unidade": unidade,
                "valor": str(valor),
                "source_type": source_type,
                "source_uri": uri,
            },
            "justificativa": razao,
        },
    )
    return fator


def atualizar_vigencia_rascunho(
    db: Session,
    parametro_set_id: int,
    vigencia_inicio: date,
    vigencia_fim: date | None,
    wordpress_user_id: int,
    justificativa: str,
    correlation_id: str | None = None,
) -> ParametroSet:
    razao = _validar_ator_e_justificativa(
        wordpress_user_id, justificativa
    )
    conjunto = _obter_rascunho(db, parametro_set_id)

    if (
        vigencia_fim is not None
        and vigencia_fim < vigencia_inicio
    ):
        raise ErroParametro(
            422,
            "VIGENCIA_INVALIDA",
            "A data final deve ser igual ou posterior a inicial.",
        )

    anterior = {
        "inicio": conjunto.vigencia_inicio.isoformat(),
        "fim": (
            conjunto.vigencia_fim.isoformat()
            if conjunto.vigencia_fim else None
        ),
    }

    conjunto.vigencia_inicio = vigencia_inicio
    conjunto.vigencia_fim = vigencia_fim
    db.flush()

    registrar_auditoria(
        db=db,
        entidade="parametro_set",
        entidade_id=conjunto.id,
        acao="ATUALIZAR",
        wordpress_user_id=wordpress_user_id,
        correlation_id=correlation_id,
        detalhes={
            "antes": anterior,
            "depois": {
                "inicio": vigencia_inicio.isoformat(),
                "fim": (
                    vigencia_fim.isoformat()
                    if vigencia_fim else None
                ),
            },
            "justificativa": razao,
        },
    )
    return conjunto
