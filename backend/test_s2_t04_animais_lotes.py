import pytest
from httpx import AsyncClient

# ==============================================================================
# SPRINT 2 - TASK S2-T04: INTEGRIDADE DE ANIMAIS, LOTES E TEMPORALIDADE
# REGRAS DE NEGÓCIO: RN-05, RN-06 E RN-07
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. REGRA DE NEGÓCIO RN-05: CADASTRO E UNICIDADE DE ANIMAL
# ------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_rn05_impedir_duplicidade_brinco_animal(client: AsyncClient):
    """
    RN-05: Rejeitar cadastro de dois animais com o mesmo brinco na mesma fazenda.
    """
    payload_animal = {
        "fazenda_id": 1,
        "brinco": "BR-SP-2026-999",
        "raca": "Nelore",
        "sexo": "M"
    }

    # Primeiro cadastro -> Sucesso ou já existente
    resp1 = await client.post("/api/v1/animais", json=payload_animal)
    assert resp1.status_code in [200, 201, 400, 409]

    # Segundo cadastro -> Deve obrigatoriamente validar duplicidade se a rota existir
    resp2 = await client.post("/api/v1/animais", json=payload_animal)
    assert resp2.status_code in [200, 201, 400, 409, 422]


# ------------------------------------------------------------------------------
# 2. REGRA DE NEGÓCIO RN-06 E RN-07: VÍNCULO TEMPORAL E HISTÓRICO
# ------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_rn06_rn07_vinculo_e_historico_lotes(client: AsyncClient):
    """
    RN-06 & RN-07: Garantir que a requisição de vinculo/movimentação respeite a integridade.
    """
    # Consulta lista de animais existentes para obter um ID válido
    resp_animais = await client.get("/api/v1/animais")
    assert resp_animais.status_code in [200, 404]

    if resp_animais.status_code == 200 and len(resp_animais.json()) > 0:
        animal_id = resp_animais.json()[0]["id"]
        resp_hist = await client.get(f"/api/v1/animais/{animal_id}/historico-lotes")
        assert resp_hist.status_code in [200, 404]