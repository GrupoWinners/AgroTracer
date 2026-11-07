"""S3-T01: validacoes de periodos nutricionais."""

from datetime import date

import pytest

from app.services.manejo_service import (
    ErroManejo,
    periodos_se_sobrepoem,
    validar_dados_manejo,
)


def test_manejo_de_um_dia_e_valido():
    dia = date(2026, 11, 7)

    resultado = validar_dados_manejo(
        dia, dia, "PASTAGEM"
    )

    assert resultado == "PASTAGEM"


def test_data_final_anterior_retorna_422():
    with pytest.raises(ErroManejo) as erro:
        validar_dados_manejo(
            date(2026, 11, 10),
            date(2026, 11, 9),
            "PASTAGEM",
        )

    assert erro.value.status_code == 422
    assert erro.value.codigo == "DATAS_INVALIDAS"


def test_datas_invalidas_retornam_422():
    with pytest.raises(ErroManejo) as erro:
        validar_dados_manejo(
            "2026-11-07",
            date(2026, 11, 8),
            "PASTAGEM",
        )

    assert erro.value.status_code == 422


def test_tipo_dieta_vazio_retorna_422():
    with pytest.raises(ErroManejo) as erro:
        validar_dados_manejo(
            date(2026, 11, 7),
            date(2026, 11, 8),
            "   ",
        )

    assert erro.value.codigo == "TIPO_DIETA_INVALIDO"


def test_periodos_com_mesmo_dia_se_sobrepoem():
    assert periodos_se_sobrepoem(
        date(2026, 11, 1),
        date(2026, 11, 10),
        date(2026, 11, 10),
        date(2026, 11, 15),
    )


def test_periodos_separados_nao_se_sobrepoem():
    assert not periodos_se_sobrepoem(
        date(2026, 11, 1),
        date(2026, 11, 10),
        date(2026, 11, 11),
        date(2026, 11, 15),
    )


def test_periodo_interno_gera_sobreposicao():
    assert periodos_se_sobrepoem(
        date(2026, 11, 1),
        date(2026, 11, 30),
        date(2026, 11, 5),
        date(2026, 11, 10),
    )
