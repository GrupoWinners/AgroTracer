import pytest
from datetime import date, timedelta
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_rn08_manejo_mesmo_dia_conta_um_dia(client: AsyncClient, lote_valido: int):
    """
    RN-08: Data de início igual à data de fim deve ser aceita e contabilizar 1 dia.
    Endpoint: POST /api/v1/lotes/{lote_id}/manejos
    """
    data_hoje = str(date.today())

    payload_manejo = {
        "inicio": data_hoje,
        "fim": data_hoje,
        "parametro_set_id": 1,
        "tipo_dieta": "CONCENTRADO"
    }

    url = f"/api/v1/lotes/{lote_valido}/manejos"
    resp = await client.post(url, json=payload_manejo)
    assert resp.status_code in [200, 201], f"Erro ao criar manejo: {resp.text}"


@pytest.mark.asyncio
async def test_rn08_impedir_data_fim_anterior_a_inicio(client: AsyncClient, lote_valido: int):
    """
    RN-08: Data de fim anterior à data de início deve ser rejeitada com HTTP 400 ou 422.
    """
    data_inicio = str(date.today())
    data_fim = str(date.today() - timedelta(days=5))

    payload_manejo = {
        "inicio": data_inicio,
        "fim": data_fim,
        "parametro_set_id": 1,
        "tipo_dieta": "SILAGEM"
    }

    url = f"/api/v1/lotes/{lote_valido}/manejos"
    resp = await client.post(url, json=payload_manejo)
    assert resp.status_code in [400, 422], f"RN-08 VIOLADA: API aceitou fim < inicio! Status: {resp.status_code}"


@pytest.mark.asyncio
async def test_rn08_impedir_sobreposicao_de_periodos(client: AsyncClient, lote_valido: int):
    """
    RN-08: Rejeitar novos manejos que se sobreponham a um período existente no mesmo lote.
    """
    url = f"/api/v1/lotes/{lote_valido}/manejos"

    # 1. Registrar manejo base
    d_inicio_1 = str(date.today() + timedelta(days=10))
    d_fim_1 = str(date.today() + timedelta(days=20))

    payload_1 = {
        "inicio": d_inicio_1,
        "fim": d_fim_1,
        "parametro_set_id": 1,
        "tipo_dieta": "PASTAGEM"
    }
    resp1 = await client.post(url, json=payload_1)
    assert resp1.status_code in [200, 201], f"Erro ao registrar manejo base: {resp1.text}"

    # 2. Tentar registrar manejo sobreposto
    d_inicio_2 = str(date.today() + timedelta(days=15))
    d_fim_2 = str(date.today() + timedelta(days=25))

    payload_2 = {
        "inicio": d_inicio_2,
        "fim": d_fim_2,
        "parametro_set_id": 1,
        "tipo_dieta": "CONCENTRADO"
    }
    resp2 = await client.post(url, json=payload_2)
    assert resp2.status_code == 409, f"RN-08 VIOLADA: API permitiu sobreposição! Status: {resp2.status_code}"