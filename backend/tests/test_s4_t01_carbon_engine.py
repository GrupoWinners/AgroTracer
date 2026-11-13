"""S4-T01: exemplo didatico e aritmetica deterministica."""

from datetime import date
from decimal import Decimal, localcontext

import pytest

from app.services.carbon_engine import (
    ErroCarbono,
    FatoresVersionados,
    PeriodoCalculo,
    calcular_emissoes,
    calcular_intensidade,
)


def fatores(valor):
    return FatoresVersionados(
        parametro_set_id=1,
        versao="DEMO-SYNTHETIC-2026-01",
        fe_base_dieta=Decimal(valor),
        k_idade=Decimal("1"),
        k_pastagem=Decimal("1"),
        k_suplementacao=Decimal("1"),
    )


def test_homologacao_sintetica_13650_e_0954():
    dados = [
        PeriodoCalculo(
            date(2026, 1, 1), date(2026, 3, 31), 50, fatores("2.10")
        ),
        PeriodoCalculo(
            date(2026, 4, 1), date(2026, 5, 30), 50, fatores("1.40")
        ),
    ]
    resultado = calcular_emissoes(dados)
    assert [x.dias for x in resultado.periodos] == [90, 60]
    assert resultado.total_kg_co2e == Decimal("13650")
    intensidade = calcular_intensidade(
        resultado.total_kg_co2e, 50, Decimal("540"), Decimal("0.53")
    )
    assert intensidade.quantize(Decimal("0.001")) == Decimal("0.954")


def test_manejo_um_dia():
    resultado = calcular_emissoes([
        PeriodoCalculo(
            date(2026, 11, 12), date(2026, 11, 12), 10,
            fatores("2.10"),
        )
    ])
    assert resultado.periodos[0].dias == 1
    assert resultado.total_kg_co2e == Decimal("21")


def test_precisao_sem_arredondar_etapas():
    f = FatoresVersionados(
        1, "DEMO", Decimal("0.123456789123"),
        Decimal("1.234567890123"),
        Decimal("1.000000000001"),
        Decimal("0.987654321987"),
    )
    total = calcular_emissoes([
        PeriodoCalculo(date(2026, 1, 1), date(2026, 1, 1), 1, f)
    ]).total_kg_co2e
    with localcontext() as ctx:
        ctx.prec = 80
        esperado = (
            f.fe_base_dieta * f.k_idade
            * f.k_pastagem * f.k_suplementacao
        )
    assert total == esperado


@pytest.mark.parametrize("quantidade,peso,rendimento", [
    (0, "540", "0.53"),
    (-1, "540", "0.53"),
    (50, "0", "0.53"),
    (50, "-10", "0.53"),
    (50, "540", "0"),
    (50, "540", "-0.1"),
])
def test_denominador_invalido_nao_divide(quantidade, peso, rendimento):
    assert calcular_intensidade(
        Decimal("13650"), quantidade,
        Decimal(peso), Decimal(rendimento)
    ) is None


def test_data_invertida_e_rejeitada():
    with pytest.raises(ErroCarbono):
        calcular_emissoes([
            PeriodoCalculo(
                date(2026, 2, 2), date(2026, 2, 1), 5,
                fatores("2.10"),
            )
        ])


def test_float_nao_e_aceito():
    f = FatoresVersionados(
        1, "DEMO", 2.10, Decimal("1"),
        Decimal("1"), Decimal("1"),
    )
    with pytest.raises(ErroCarbono):
        calcular_emissoes([
            PeriodoCalculo(
                date(2026, 1, 1), date(2026, 1, 1), 1, f
            )
        ])
