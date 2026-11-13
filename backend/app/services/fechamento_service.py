"""S4-T02: pre-condicoes de fechamento (RN-09/RN-10/RN-21)."""

from datetime import datetime, time, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.estados_lote import (
    EstadoLote, TransicaoLoteInvalida, validar_transicao_lote,
)
from app.models.fechamento_lote import FechamentoLote
from app.models.lote import Lote
from app.models.lote_animal import LoteAnimal
from app.models.manejo_nutricional import ManejoNutricional
from app.models.parametro_set import ParametroSet
from app.schemas.fechamento import FechamentoEntrada
from app.services.audit_service import registrar_auditoria
from app.services.carbon_engine import (
    ErroCarbono, PeriodoCalculo,
    calcular_emissoes, calcular_intensidade,
)
from app.services.carbon_fatores_service import carregar_fatores_versionados
from app.services.snapshot_service import persistir_snapshot_fechamento


class ErroFechamento(Exception):
    def __init__(self, status_code: int, codigo: str, mensagem: str):
        self.status_code = status_code
        self.codigo = codigo
        self.mensagem = mensagem
        super().__init__(mensagem)


def _contar_animais_periodo(associacoes, inicio, fim) -> int:
    """Exige associacoes completas por dia; rejeita mudancas parciais."""
    inicio_dt = datetime.combine(inicio, time.min, tzinfo=timezone.utc)
    try:
        fim_exclusivo = datetime.combine(
            fim + timedelta(days=1), time.min, tzinfo=timezone.utc,
        )
    except OverflowError as erro:
        raise ErroFechamento(
            422, "PERIODO_INVALIDO", "Data final fora do intervalo.",
        ) from erro
    animais = set()
    for associacao in associacoes:
        entrada = associacao.associado_em
        saida = associacao.desassociado_em
        if entrada.tzinfo is None:
            entrada = entrada.replace(tzinfo=timezone.utc)
        if saida is not None and saida.tzinfo is None:
            saida = saida.replace(tzinfo=timezone.utc)
        if entrada >= fim_exclusivo or (
            saida is not None and saida <= inicio_dt
        ):
            continue
        if entrada > inicio_dt or (
            saida is not None and saida < fim_exclusivo
        ):
            raise ErroFechamento(
                422, "ASSOCIACOES_PARCIAIS",
                "Associacao mudou no meio do manejo. "
                "Divida o periodo antes de fechar.",
            )
        if associacao.animal_id in animais:
            raise ErroFechamento(
                422, "ASSOCIACAO_DUPLICADA",
                "Animal duplicado no mesmo periodo de manejo.",
            )
        animais.add(associacao.animal_id)
    if not animais:
        raise ErroFechamento(
            422, "ASSOCIACOES_AUSENTES",
            "Manejo sem animais vinculados durante todo o periodo.",
        )
    return len(animais)


def registrar_fechamento(
    db: Session,
    lote: Lote,
    dados: FechamentoEntrada,
    wp_user_id: int,
    correlation_id: str | None,
) -> FechamentoLote:
    """O chamador bloqueia e autoriza o lote; commit somente na rota."""
    try:
        validar_transicao_lote(
            EstadoLote(lote.status), EstadoLote.FECHADO,
        )
    except (ValueError, TransicaoLoteInvalida) as erro:
        raise ErroFechamento(
            409, "LOTE_ESTADO_INVALIDO",
            "Somente lotes EM_MANEJO podem ser fechados.",
        ) from erro

    if db.scalar(select(FechamentoLote.id).where(
        FechamentoLote.lote_id == lote.id,
    )) is not None:
        raise ErroFechamento(
            409, "LOTE_JA_FECHADO", "Lote ja possui fechamento.",
        )

    manejos = db.scalars(
        select(ManejoNutricional)
        .where(ManejoNutricional.lote_id == lote.id)
        .order_by(ManejoNutricional.inicio)
    ).all()
    if not manejos:
        raise ErroFechamento(
            422, "MANEJO_OBRIGATORIO", "Registre ao menos um manejo.",
        )
    if dados.data_abate < max(manejo.fim for manejo in manejos):
        raise ErroFechamento(
            422, "ABATE_ANTERIOR_AO_MANEJO",
            "Data de abate anterior ao fim do manejo.",
        )
    sets = {manejo.parametro_set_id for manejo in manejos}
    if len(sets) != 1:
        raise ErroFechamento(
            422, "VERSOES_MULTIPLAS",
            "O fechamento MVP exige um unico conjunto versionado.",
        )
    parametro_set_id = next(iter(sets))
    conjunto = db.get(ParametroSet, parametro_set_id)
    if conjunto is None or conjunto.status == "RASCUNHO":
        raise ErroFechamento(
            422, "PARAMETROS_NAO_PUBLICADOS",
            "Publique o conjunto de fatores antes do fechamento.",
        )
    if any(
        manejo.inicio < conjunto.vigencia_inicio
        or (conjunto.vigencia_fim is not None
            and manejo.fim > conjunto.vigencia_fim)
        for manejo in manejos
    ):
        raise ErroFechamento(
            422, "PARAMETROS_FORA_VIGENCIA",
            "Manejo fora da vigencia dos parametros.",
        )

    associacoes = db.scalars(
        select(LoteAnimal).where(LoteAnimal.lote_id == lote.id)
    ).all()
    periodos = []
    for manejo in manejos:
        quantidade = _contar_animais_periodo(
            associacoes, manejo.inicio, manejo.fim,
        )
        try:
            fatores = carregar_fatores_versionados(
                db, manejo.parametro_set_id, manejo.tipo_dieta,
            )
        except ErroCarbono as erro:
            raise ErroFechamento(
                422, "FATORES_INVALIDOS", str(erro),
            ) from erro
        periodos.append(PeriodoCalculo(
            manejo.inicio, manejo.fim, quantidade, fatores,
        ))
    if dados.numero_animais_abate > periodos[-1].numero_animais:
        raise ErroFechamento(
            422, "ABATE_SUPERIOR_AOS_ANIMAIS",
            "Quantidade abatida excede animais do ultimo manejo.",
        )

    try:
        resultado = calcular_emissoes(periodos)
        intensidade = calcular_intensidade(
            resultado.total_kg_co2e,
            dados.numero_animais_abate,
            dados.peso_medio_abate_kg,
            dados.rendimento_carcaca,
        )
    except ErroCarbono as erro:
        raise ErroFechamento(
            422, "CALCULO_INVALIDO", str(erro),
        ) from erro
    if intensidade is None:
        raise ErroFechamento(
            422, "INTENSIDADE_NAO_CALCULAVEL",
            "Denominador invalido para intensidade.",
        )

    fechamento = FechamentoLote(
        lote_id=lote.id,
        parametro_set_id=parametro_set_id,
        versao_metodo=resultado.versao_metodo,
        data_abate=dados.data_abate,
        numero_animais_abate=dados.numero_animais_abate,
        peso_medio_abate_kg=dados.peso_medio_abate_kg,
        rendimento_carcaca=dados.rendimento_carcaca,
        emissao_total_kg_co2e=resultado.total_kg_co2e,
        intensidade_kg_co2e_kg=intensidade,
    )
    db.add(fechamento)
    db.flush()
    lote.status = EstadoLote.FECHADO.value

    persistir_snapshot_fechamento(
        db, fechamento, dados, resultado, intensidade,
    )

    registrar_auditoria(
        db=db, entidade="fechamentos_lote",
        acao="FECHAR_LOTE", entidade_id=fechamento.id,
        wordpress_user_id=wp_user_id,
        correlation_id=correlation_id,
        detalhes={
            "lote_id": lote.id,
            "parametro_set_id": parametro_set_id,
            "versao_metodo": resultado.versao_metodo,
        },
    )
    db.flush()
    return fechamento
