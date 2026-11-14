"""S4-T05: Casos limite, tabela de expected results e precisao analitica.

Valida a estabilidade aritmetica do CarbonEngine diante de entradas limites:
zero, negativos, temporalidade anomala, denominadores invalidos e precisao.
"""

from datetime import date, datetime
from decimal import Decimal, localcontext

import pytest

from app.services.carbon_engine import (
    VERSAO_METODO,
    ErroCarbono,
    FatoresVersionados,
    PeriodoCalculo,
    calcular_emissoes,
    calcular_intensidade,
)


def _fatores_teste(
    fe_base="2.10",
    k_idade="1",
    k_pastagem="1",
    k_suplementacao="1",
    parametro_set_id=1,
    versao="DEMO-S4-T05",
    fe_base_dieta=None,
):
    """Cria fatores versionados validos para cenarios de teste."""
    valor_fe = fe_base_dieta if fe_base_dieta is not None else fe_base
    return FatoresVersionados(
        parametro_set_id=parametro_set_id,
        versao=versao,
        fe_base_dieta=Decimal(str(valor_fe)),
        k_idade=Decimal(str(k_idade)),
        k_pastagem=Decimal(str(k_pastagem)),
        k_suplementacao=Decimal(str(k_suplementacao)),
    )


# ============================================================================
# 1. TABELA DE EXPECTED RESULTS (CALCULO MANUAL DETERMINISTICO)
# ============================================================================


def test_expected_result_caso_base_sintetico():
    """Valida o caso de referencia com 2 periodos sinteticos.

    Periodo 1: 50 cabecas x 90 dias x (2.10 * 1 * 1 * 1) = 9.450 kg CO2e
    Periodo 2: 50 cabecas x 60 dias x (1.40 * 1 * 1 * 1) = 4.200 kg CO2e
    Total Emissoes: 13.650 kg CO2e
    Carcaça: 50 cabecas * 540 kg * 0.53 = 14.310 kg
    Intensidade: 13.650 / 14.310 = ~0.9538784... kg CO2e / kg carcaça
    """
    p1 = PeriodoCalculo(
        date(2026, 1, 1), date(2026, 3, 31), 50, _fatores_teste("2.10")
    )
    p2 = PeriodoCalculo(
        date(2026, 4, 1), date(2026, 5, 30), 50, _fatores_teste("1.40")
    )

    res = calcular_emissoes([p1, p2])

    assert res.versao_metodo == VERSAO_METODO
    assert len(res.periodos) == 2
    assert res.periodos[0].dias == 90
    assert res.periodos[0].emissao_kg_co2e == Decimal("9450")
    assert res.periodos[1].dias == 60
    assert res.periodos[1].emissao_kg_co2e == Decimal("4200")
    assert res.total_kg_co2e == Decimal("13650")

    intensidade = calcular_intensidade(
        res.total_kg_co2e, 50, Decimal("540"), Decimal("0.53")
    )
    assert intensidade is not None
    assert intensidade.quantize(Decimal("0.001")) == Decimal("0.954")
    assert intensidade.quantize(Decimal("0.000001")) == Decimal("0.953878")


def test_expected_result_multiplicadores_combinados():
    """Calculo manual com multiplicadores compostos e dias inclusivos.

    Periodo: 2026-06-01 a 2026-06-10 (10 dias), 20 animais.
    fe_base = 2.50
    k_idade = 1.20
    k_pastagem = 0.85
    k_suplementacao = 1.10
    fe_ajustado = 2.50 * 1.20 * 0.85 * 1.10 = 2.80500
    emissao = 10 * 20 * 2.80500 = 561.00000 kg CO2e
    """
    fatores = _fatores_teste(
        fe_base="2.50",
        k_idade="1.20",
        k_pastagem="0.85",
        k_suplementacao="1.10",
    )
    periodo = PeriodoCalculo(
        date(2026, 6, 1), date(2026, 6, 10), 20, fatores
    )
    res = calcular_emissoes([periodo])

    assert res.periodos[0].dias == 10
    assert res.periodos[0].fe_ajustado == Decimal("2.805")
    assert res.periodos[0].emissao_kg_co2e == Decimal("561")
    assert res.total_kg_co2e == Decimal("561")


# ============================================================================
# 2. CASOS LIMITE: ZERO
# ============================================================================


def test_zero_animais_no_manejo():
    """Lote vazio durante periodo de manejo: emissao deve ser 0 kg CO2e."""
    periodo = PeriodoCalculo(
        date(2026, 1, 1), date(2026, 1, 31), 0, _fatores_teste("2.10")
    )
    res = calcular_emissoes([periodo])
    assert res.periodos[0].numero_animais == 0
    assert res.periodos[0].emissao_kg_co2e == Decimal("0")
    assert res.total_kg_co2e == Decimal("0")


def test_zero_fator_emissao_base():
    """Dieta com emissao base zero resulta em emissao zero."""
    periodo = PeriodoCalculo(
        date(2026, 1, 1), date(2026, 1, 10), 100, _fatores_teste("0")
    )
    res = calcular_emissoes([periodo])
    assert res.periodos[0].fe_ajustado == Decimal("0")
    assert res.total_kg_co2e == Decimal("0")


def test_zero_multiplicador_zera_emissao():
    """Multiplicador zero anula a emissao do periodo."""
    fatores = _fatores_teste(fe_base="2.10", k_suplementacao="0")
    periodo = PeriodoCalculo(
        date(2026, 1, 1), date(2026, 1, 15), 50, fatores
    )
    res = calcular_emissoes([periodo])
    assert res.periodos[0].fe_ajustado == Decimal("0")
    assert res.total_kg_co2e == Decimal("0")


def test_zero_emissao_total_com_abate_valido():
    """Emissao zero dividida por carcaça valida resulta em intensidade 0."""
    intensidade = calcular_intensidade(
        Decimal("0"), 50, Decimal("540"), Decimal("0.53")
    )
    assert intensidade == Decimal("0")


@pytest.mark.parametrize(
    "animais,peso,rendimento",
    [
        (0, "540", "0.53"),
        (50, "0", "0.53"),
        (50, "540", "0"),
        (0, "0", "0"),
    ],
)
def test_zero_no_denominador_retorna_none_sem_divisao_por_zero(
    animais, peso, rendimento
):
    """Denominador zero deve retornar None e nunca lancar ZeroDivisionError."""
    resultado = calcular_intensidade(
        Decimal("13650"), animais, Decimal(peso), Decimal(rendimento)
    )
    assert resultado is None


# ============================================================================
# 3. CASOS LIMITE: NEGATIVOS
# ============================================================================


def test_negativo_animais_manejo_rejeitado():
    """Quantidade negativa de animais no manejo deve lancar ErroCarbono."""
    with pytest.raises(ErroCarbono, match="Quantidade de animais invalida"):
        calcular_emissoes([
            PeriodoCalculo(
                date(2026, 1, 1), date(2026, 1, 10), -5, _fatores_teste()
            )
        ])


@pytest.mark.parametrize(
    "campo,valor",
    [
        ("fe_base_dieta", "-0.01"),
        ("k_idade", "-1.0"),
        ("k_pastagem", "-0.5"),
        ("k_suplementacao", "-0.0001"),
    ],
)
def test_negativo_fatores_rejeitados(campo, valor):
    """Fatores com valor negativo devem lancar ErroCarbono."""
    kwargs = {campo: valor}
    with pytest.raises(ErroCarbono, match="nao pode ser negativo"):
        calcular_emissoes([
            PeriodoCalculo(
                date(2026, 1, 1),
                date(2026, 1, 10),
                10,
                _fatores_teste(**kwargs),
            )
        ])


def test_negativo_emissao_total_em_intensidade():
    """Emissao negativa em calcular_intensidade lanca ErroCarbono."""
    with pytest.raises(
        ErroCarbono, match="emissao_total nao pode ser negativo"
    ):
        calcular_intensidade(
            Decimal("-100"), 50, Decimal("540"), Decimal("0.53")
        )


@pytest.mark.parametrize(
    "animais,peso,rendimento",
    [
        (-1, "540", "0.53"),
        (50, "-540", "0.53"),
        (50, "540", "-0.53"),
        (-10, "-100", "-0.5"),
    ],
)
def test_negativo_parametros_abate_retornam_none(
    animais, peso, rendimento
):
    """Valores negativos de abate no denominador devem retornar None."""
    assert (
        calcular_intensidade(
            Decimal("13650"), animais, Decimal(peso), Decimal(rendimento)
        )
        is None
    )


# ============================================================================
# 4. CASOS LIMITE: TEMPORAIS
# ============================================================================


def test_temporal_mesmo_dia_inclusivo():
    """Manejo de um unico dia (inicio == fim) contabiliza exatamente 1 dia."""
    periodo = PeriodoCalculo(
        date(2026, 7, 15), date(2026, 7, 15), 30, _fatores_teste("2.00")
    )
    res = calcular_emissoes([periodo])
    assert res.periodos[0].dias == 1
    assert res.periodos[0].emissao_kg_co2e == Decimal("60")  # 1 * 30 * 2.00
    assert res.total_kg_co2e == Decimal("60")


def test_temporal_fim_menor_que_inicio_rejeitado():
    """Data final anterior ao inicio deve ser rejeitada com ErroCarbono."""
    with pytest.raises(ErroCarbono, match="Datas invalidas para manejo"):
        calcular_emissoes([
            PeriodoCalculo(
                date(2026, 8, 10),
                date(2026, 8, 9),
                10,
                _fatores_teste(),
            )
        ])


def test_temporal_ano_bissexto():
    """Ano bissexto: fevereiro de 2024 (29 dias inclusivos)."""
    periodo = PeriodoCalculo(
        date(2024, 2, 1), date(2024, 2, 29), 10, _fatores_teste("1.00")
    )
    res = calcular_emissoes([periodo])
    assert res.periodos[0].dias == 29
    assert res.total_kg_co2e == Decimal("290")


def test_temporal_virada_de_ano():
    """Manejo cruzando virada de ano (15/12 a 15/01 inclusivos = 32 dias)."""
    periodo = PeriodoCalculo(
        date(2025, 12, 15), date(2026, 1, 15), 10, _fatores_teste("1.00")
    )
    res = calcular_emissoes([periodo])
    assert res.periodos[0].dias == 32
    assert res.total_kg_co2e == Decimal("320")


@pytest.mark.parametrize(
    "dt_inicio,dt_fim",
    [
        ("2026-01-01", date(2026, 1, 10)),
        (date(2026, 1, 1), "2026-01-10"),
        (datetime(2026, 1, 1, 10, 0), date(2026, 1, 10)),
        (None, date(2026, 1, 10)),
        (date(2026, 1, 1), None),
    ],
)
def test_temporal_tipos_invalidos_rejeitados(dt_inicio, dt_fim):
    """Datas que nao sejam estritamente datetime.date devem ser rejeitadas."""
    with pytest.raises(ErroCarbono, match="Datas invalidas para manejo"):
        calcular_emissoes([
            PeriodoCalculo(dt_inicio, dt_fim, 10, _fatores_teste())
        ])


# ============================================================================
# 5. CASOS LIMITE: TIPOS, FLOATS E ESTRUTURA
# ============================================================================


def test_lista_vazia_de_periodos_rejeitada():
    """Calculo sem periodos deve lancar ErroCarbono."""
    with pytest.raises(ErroCarbono, match="E necessario ao menos um periodo"):
        calcular_emissoes([])


def test_float_em_fator_rejeitado():
    """Contaminacao por float deve ser estritamente bloqueada."""
    fatores = FatoresVersionados(
        1,
        "DEMO",
        2.10,  # float proibido
        Decimal("1"),
        Decimal("1"),
        Decimal("1"),
    )
    with pytest.raises(ErroCarbono, match="deve ser Decimal finito"):
        calcular_emissoes([
            PeriodoCalculo(date(2026, 1, 1), date(2026, 1, 5), 10, fatores)
        ])


@pytest.mark.parametrize(
    "valor_invalido",
    [
        Decimal("NaN"),
        Decimal("Infinity"),
        Decimal("-Infinity"),
    ],
)
def test_decimal_nao_finito_rejeitado(valor_invalido):
    """Decimais infinitos ou NaN devem ser rejeitados."""
    with pytest.raises(ErroCarbono, match="deve ser Decimal finito"):
        calcular_emissoes([
            PeriodoCalculo(
                date(2026, 1, 1),
                date(2026, 1, 5),
                10,
                _fatores_teste(fe_base=valor_invalido),
            )
        ])


@pytest.mark.parametrize("animais_invalido", ["50", 50.0, None, [50]])
def test_tipo_invalido_numero_animais_manejo(animais_invalido):
    """Numero de animais no manejo que nao seja int estrito e rejeitado."""
    with pytest.raises(ErroCarbono, match="Quantidade de animais invalida"):
        calcular_emissoes([
            PeriodoCalculo(
                date(2026, 1, 1),
                date(2026, 1, 5),
                animais_invalido,
                _fatores_teste(),
            )
        ])


@pytest.mark.parametrize("animais_abate", ["50", 50.5, None])
def test_tipo_invalido_animais_abate_intensidade(animais_abate):
    """Animais de abate nao inteiro em calcular_intensidade lanca erro."""
    with pytest.raises(
        ErroCarbono, match="Quantidade de animais de abate invalida"
    ):
        calcular_intensidade(
            Decimal("13650"), animais_abate, Decimal("540"), Decimal("0.53")
        )


@pytest.mark.parametrize(
    "peso,rendimento",
    [
        (540.0, Decimal("0.53")),
        ("540", Decimal("0.53")),
        (Decimal("540"), 0.53),
        (Decimal("540"), "0.53"),
    ],
)
def test_peso_ou_rendimento_nao_decimal_lanca_erro(peso, rendimento):
    """Peso e rendimento devem ser obrigatoriamente instâncias de Decimal."""
    with pytest.raises(ErroCarbono, match="deve ser Decimal"):
        calcular_intensidade(Decimal("13650"), 50, peso, rendimento)


@pytest.mark.parametrize(
    "parametro_set_id,versao",
    [
        (0, "V1"),
        (-1, "V1"),
        (1, ""),
        (1, "   "),
    ],
)
def test_identificacao_fatores_invalida(parametro_set_id, versao):
    """Parametro set ID <= 0 ou versao vazia devem ser rejeitados."""
    fatores = _fatores_teste(
        parametro_set_id=parametro_set_id,
        versao=versao,
    )
    with pytest.raises(
        ErroCarbono, match="Identificacao dos fatores invalida"
    ):
        calcular_emissoes([
            PeriodoCalculo(date(2026, 1, 1), date(2026, 1, 5), 10, fatores)
        ])


# ============================================================================
# 6. CASOS LIMITE: PRECISÃO DECIMAL E AUSÊNCIA DE ARREDONDAMENTO INTERMEDIÁRIO
# ============================================================================


def test_alta_precisao_analitica_sem_arredondamento():
    """Garante que todas as 80 casas decimais do contexto sao preservadas."""
    f = FatoresVersionados(
        parametro_set_id=1,
        versao="HI-PRECISION",
        fe_base_dieta=Decimal("2.12345678901234567890"),
        k_idade=Decimal("1.09876543210987654321"),
        k_pastagem=Decimal("0.98765432109876543210"),
        k_suplementacao=Decimal("1.00000000000000000001"),
    )
    periodo = PeriodoCalculo(date(2026, 1, 1), date(2026, 1, 7), 13, f)

    res = calcular_emissoes([periodo])

    with localcontext() as ctx:
        ctx.prec = 80
        esperado_fe = (
            f.fe_base_dieta
            * f.k_idade
            * f.k_pastagem
            * f.k_suplementacao
        )
        esperado_emissao = Decimal(7) * 13 * esperado_fe

    assert res.periodos[0].dias == 7
    assert res.periodos[0].fe_ajustado == esperado_fe
    assert res.periodos[0].emissao_kg_co2e == esperado_emissao
    assert res.total_kg_co2e == esperado_emissao


def test_comutatividade_multiplicadores():
    """A multiplicacao dos fatores e comutativa e deterministica."""
    f1 = _fatores_teste("2.10", "1.10", "0.90", "1.05")
    f2 = _fatores_teste("2.10", "1.05", "1.10", "0.90")
    f3 = _fatores_teste("2.10", "0.90", "1.05", "1.10")

    p1 = PeriodoCalculo(date(2026, 1, 1), date(2026, 1, 10), 10, f1)
    p2 = PeriodoCalculo(date(2026, 1, 1), date(2026, 1, 10), 10, f2)
    p3 = PeriodoCalculo(date(2026, 1, 1), date(2026, 1, 10), 10, f3)

    r1 = calcular_emissoes([p1]).total_kg_co2e
    r2 = calcular_emissoes([p2]).total_kg_co2e
    r3 = calcular_emissoes([p3]).total_kg_co2e

    assert r1 == r2 == r3
