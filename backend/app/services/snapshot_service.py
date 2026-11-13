"""S4-T03: captura fiel e versionada dos inputs e resultados."""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.snapshot_fechamento import SnapshotFechamento


def _decimal_texto(valor: Decimal) -> str:
    return format(valor, "f")


def persistir_snapshot_fechamento(
    db: Session,
    fechamento,
    dados,
    resultado,
    intensidade: Decimal,
) -> SnapshotFechamento:
    """Nao faz commit; fechamento/auditoria/snapshot sao atomicos."""
    periodos = []
    resultados_periodos = []
    for periodo in resultado.periodos:
        fatores = periodo.fatores
        periodos.append({
            "inicio": periodo.inicio.isoformat(),
            "fim": periodo.fim.isoformat(),
            "dias": periodo.dias,
            "numero_animais": periodo.numero_animais,
            "parametro_set_id": fatores.parametro_set_id,
            "versao_parametros": fatores.versao,
            "fatores": {
                "FE_BASE_DIETA": _decimal_texto(fatores.fe_base_dieta),
                "K_IDADE": _decimal_texto(fatores.k_idade),
                "K_PASTAGEM": _decimal_texto(fatores.k_pastagem),
                "K_SUPLEMENTACAO": _decimal_texto(
                    fatores.k_suplementacao
                ),
            },
            "proveniencia": [
                {"chave": chave, "source_type": tipo,
                 "source_uri": uri or None, "unidade": unidade}
                for chave, tipo, uri, unidade in fatores.proveniencia
            ],
        })
        resultados_periodos.append({
            "inicio": periodo.inicio.isoformat(),
            "fim": periodo.fim.isoformat(),
            "dias": periodo.dias,
            "numero_animais": periodo.numero_animais,
            "fe_ajustado": _decimal_texto(periodo.fe_ajustado),
            "emissao_kg_co2e": _decimal_texto(
                periodo.emissao_kg_co2e
            ),
        })

    entradas = {
        "data_abate": dados.data_abate.isoformat(),
        "numero_animais_abate": dados.numero_animais_abate,
        "peso_medio_abate_kg": _decimal_texto(
            dados.peso_medio_abate_kg
        ),
        "rendimento_carcaca": _decimal_texto(
            dados.rendimento_carcaca
        ),
        "periodos": periodos,
    }
    resultados = {
        "periodos": resultados_periodos,
        "emissao_total_kg_co2e": _decimal_texto(
            resultado.total_kg_co2e
        ),
        "intensidade_kg_co2e_kg": _decimal_texto(intensidade),
    }
    snapshot = SnapshotFechamento(
        fechamento_id=fechamento.id,
        lote_id=fechamento.lote_id,
        parametro_set_id=fechamento.parametro_set_id,
        versao_parametros=resultado.periodos[0].fatores.versao,
        versao_metodo=resultado.versao_metodo,
        entradas=entradas,
        resultados=resultados,
    )
    db.add(snapshot)
    db.flush()
    return snapshot
