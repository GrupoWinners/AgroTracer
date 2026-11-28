"""S4-T01: calculo didatico deterministico com Decimal e dias inclusivos."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, localcontext


VERSAO_METODO = "CARBONENGINE-MVP-1.0"


class ErroCarbono(ValueError):
    """Entrada inadequada para um calculo de emissao."""


@dataclass(frozen=True)
class FatoresVersionados:
    parametro_set_id: int
    versao: str
    fe_base_dieta: Decimal
    k_idade: Decimal
    k_pastagem: Decimal
    k_suplementacao: Decimal
    proveniencia: tuple[tuple[str, str, str, str], ...] = ()


@dataclass(frozen=True)
class PeriodoCalculo:
    inicio: date
    fim: date
    numero_animais: int
    fatores: FatoresVersionados


@dataclass(frozen=True)
class ResultadoPeriodo:
    inicio: date
    fim: date
    dias: int
    numero_animais: int
    fatores: FatoresVersionados
    fe_ajustado: Decimal
    emissao_kg_co2e: Decimal


@dataclass(frozen=True)
class ResultadoEmissoes:
    versao_metodo: str
    periodos: tuple[ResultadoPeriodo, ...]
    total_kg_co2e: Decimal


def _validar_decimal(valor: Decimal, campo: str) -> None:
    if not isinstance(valor, Decimal) or not valor.is_finite():
        raise ErroCarbono(f"{campo} deve ser Decimal finito.")
    if valor < 0:
        raise ErroCarbono(f"{campo} nao pode ser negativo.")


def calcular_emissoes(
    periodos: list[PeriodoCalculo] | tuple[PeriodoCalculo, ...],
) -> ResultadoEmissoes:
    """Nunca arredonda periodos nem fatores durante o calculo."""
    if not periodos:
        raise ErroCarbono("E necessario ao menos um periodo.")

    resultados = []
    with localcontext() as ctx:
        ctx.prec = 80
        total = Decimal("0")
        for periodo in periodos:
            if (
                type(periodo.inicio) is not date
                or type(periodo.fim) is not date
                or periodo.fim < periodo.inicio
            ):
                raise ErroCarbono("Datas invalidas para manejo.")
            if (
                type(periodo.numero_animais) is not int
                or periodo.numero_animais < 0
            ):
                raise ErroCarbono("Quantidade de animais invalida.")
            fatores = periodo.fatores
            if (
                type(fatores.parametro_set_id) is not int
                or fatores.parametro_set_id <= 0
                or not fatores.versao.strip()
            ):
                raise ErroCarbono("Identificacao dos fatores invalida.")
            for campo in (
                "fe_base_dieta", "k_idade",
                "k_pastagem", "k_suplementacao",
            ):
                _validar_decimal(getattr(fatores, campo), campo)
            dias = (periodo.fim - periodo.inicio).days + 1
            ajustado = (
                fatores.fe_base_dieta * fatores.k_idade
                * fatores.k_pastagem * fatores.k_suplementacao
            )
            emissao = Decimal(dias) * periodo.numero_animais * ajustado
            total += emissao
            resultados.append(ResultadoPeriodo(
                inicio=periodo.inicio,
                fim=periodo.fim,
                dias=dias,
                numero_animais=periodo.numero_animais,
                fatores=fatores,
                fe_ajustado=ajustado,
                emissao_kg_co2e=emissao,
            ))

    return ResultadoEmissoes(
        versao_metodo=VERSAO_METODO,
        periodos=tuple(resultados),
        total_kg_co2e=total,
    )


def calcular_intensidade(
    emissao_total: Decimal,
    numero_animais_abate: int,
    peso_medio_abate_kg: Decimal,
    rendimento_carcaca: Decimal,
) -> Decimal | None:
    """Denominador invalido retorna None; jamais divide por zero."""
    _validar_decimal(emissao_total, "emissao_total")
    if type(numero_animais_abate) is not int:
        raise ErroCarbono("Quantidade de animais de abate invalida.")
    for nome, valor in (
        ("peso_medio_abate_kg", peso_medio_abate_kg),
        ("rendimento_carcaca", rendimento_carcaca),
    ):
        if not isinstance(valor, Decimal):
            raise ErroCarbono(f"{nome} deve ser Decimal.")
    if (
        numero_animais_abate <= 0
        or not peso_medio_abate_kg.is_finite()
        or not rendimento_carcaca.is_finite()
        or peso_medio_abate_kg <= 0
        or rendimento_carcaca <= 0
    ):
        return None
    with localcontext() as ctx:
        ctx.prec = 80
        denominador = (
            Decimal(numero_animais_abate)
            * peso_medio_abate_kg
            * rendimento_carcaca
        )
        return emissao_total / denominador
