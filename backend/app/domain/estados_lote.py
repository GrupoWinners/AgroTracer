from enum import Enum


class EstadoLote(str, Enum):
    RASCUNHO = "RASCUNHO"
    EM_MANEJO = "EM_MANEJO"
    FECHADO = "FECHADO"


TRANSICOES_PERMITIDAS = {
    EstadoLote.RASCUNHO: {EstadoLote.EM_MANEJO},
    EstadoLote.EM_MANEJO: {EstadoLote.FECHADO},
    EstadoLote.FECHADO: set(),
}


class TransicaoLoteInvalida(ValueError):
    codigo = "LOTE_TRANSICAO_INVALIDA"


def validar_transicao_lote(
    estado_atual: EstadoLote,
    novo_estado: EstadoLote,
) -> None:
    permitidos = TRANSICOES_PERMITIDAS[estado_atual]

    if novo_estado not in permitidos:
        raise TransicaoLoteInvalida(
            f"Transicao de {estado_atual.value} "
            f"para {novo_estado.value} nao permitida."
        )
