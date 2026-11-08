"""S3-T01: regras de manejo nutricional (RN-08)."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.lote import Lote
from app.models.manejo_nutricional import ManejoNutricional
from app.models.parametro_set import ParametroSet


class ErroManejo(Exception):
    def __init__(
        self,
        status_code: int,
        codigo: str,
        mensagem: str,
        detalhes: dict | None = None,
    ):
        self.status_code = status_code
        self.codigo = codigo
        self.mensagem = mensagem
        self.detalhes = detalhes or {}
        super().__init__(mensagem)


def validar_dados_manejo(
    inicio: date,
    fim: date,
    tipo_dieta: str,
) -> str:
    if type(inicio) is not date or type(fim) is not date:
        raise ErroManejo(
            422,
            "DATAS_INVALIDAS",
            "Informe datas validas no formato AAAA-MM-DD.",
        )

    if fim < inicio:
        raise ErroManejo(
            422,
            "DATAS_INVALIDAS",
            "A data final nao pode ser anterior a inicial.",
        )

    if not isinstance(tipo_dieta, str):
        raise ErroManejo(
            422,
            "TIPO_DIETA_INVALIDO",
            "Informe o tipo de dieta.",
        )

    dieta = tipo_dieta.strip()

    if not 1 <= len(dieta) <= 50:
        raise ErroManejo(
            422,
            "TIPO_DIETA_INVALIDO",
            "O tipo de dieta deve ter de 1 a 50 caracteres.",
        )

    return dieta


def periodos_se_sobrepoem(
    inicio_a: date,
    fim_a: date,
    inicio_b: date,
    fim_b: date,
) -> bool:
    """Compara periodos com datas inclusivas."""
    return inicio_a <= fim_b and inicio_b <= fim_a


def registrar_manejo(
    db: Session,
    lote_id: int,
    inicio: date,
    fim: date,
    parametro_set_id: int,
    tipo_dieta: str,
) -> ManejoNutricional:
    """Registra manejo com dupla protecao contra sobreposicao.

    O chamador deve validar a autorizacao sobre o lote
    e realizar commit ou rollback da transacao.
    """

    dieta = validar_dados_manejo(inicio, fim, tipo_dieta)

    # Bloqueia o lote durante a operacao para serializar
    # criacoes que passam por este service.
    lote_encontrado = db.scalar(
        select(Lote.id)
        .where(Lote.id == lote_id)
        .with_for_update()
    )

    if lote_encontrado is None:
        raise ErroManejo(
            404,
            "LOTE_NAO_ENCONTRADO",
            "Lote nao encontrado.",
        )

    conjunto_encontrado = db.scalar(
        select(ParametroSet.id)
        .where(ParametroSet.id == parametro_set_id)
    )

    if conjunto_encontrado is None:
        raise ErroManejo(
            404,
            "PARAMETRO_SET_NAO_ENCONTRADO",
            "Conjunto de parametros nao encontrado.",
        )

    # Service: sobreposicao inclusiva.
    # [01, 10] e [10, 15] possuem conflito.
    conflito = db.scalar(
        select(ManejoNutricional)
        .where(
            ManejoNutricional.lote_id == lote_id,
            ManejoNutricional.inicio <= fim,
            ManejoNutricional.fim >= inicio,
        )
        .order_by(ManejoNutricional.inicio)
        .limit(1)
    )

    if conflito is not None:
        raise ErroManejo(
            409,
            "MANEJO_SOBREPOSTO",
            "Existe sobreposicao com um manejo ja registrado.",
            detalhes={
                "manejo_conflitante_id": conflito.id,
                "inicio": conflito.inicio.isoformat(),
                "fim": conflito.fim.isoformat(),
            },
        )

    manejo = ManejoNutricional(
        lote_id=lote_id,
        inicio=inicio,
        fim=fim,
        parametro_set_id=parametro_set_id,
        tipo_dieta=dieta,
    )

    db.add(manejo)

    try:
        # Banco: EXCLUDE GiST protege contra concorrencia
        # mesmo se outra operacao ignorar o service.
        db.flush()

    except IntegrityError as erro:
        if getattr(erro.orig, "sqlstate", None) == "23P01":
            raise ErroManejo(
                409,
                "MANEJO_SOBREPOSTO",
                "Existe sobreposicao com um manejo ja registrado.",
            ) from erro

        raise

    return manejo
