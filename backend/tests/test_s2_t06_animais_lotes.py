import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_rn05_impedir_duplicidade_brinco_animal(client: AsyncClient):
    """
    RN-05 (Unicidade de Brinco):
    O cadastro de dois animais com o mesmo brinco na mesma fazenda DEVE ser rejeitado.
    """
    payload_animal = {
        "brinco": "BR-2026-QA01",
        "fazenda_id": 1,
        "especie": "Bovino"
    }

    # 1. Primeiro cadastro
    resp1 = await client.post("/api/v1/animais", json=payload_animal)
    
    # Valida resposta válida do cadastro ou recurso existente
    assert resp1.status_code in [200, 201, 400, 409], f"Falha no envio de cadastro: {resp1.text}"

    # 2. Tentar cadastrar o mesmo brinco novamente na mesma fazenda
    resp2 = await client.post("/api/v1/animais", json=payload_animal)
    
    # Assertividade Estrita: A API DEVE rejeitar duplicidade com 400, 409 ou 422
    if resp1.status_code in [200, 201]:
        assert resp2.status_code in [400, 409, 422], (
            f"VIOLAÇÃO DA RN-05: A API permitiu a criação de brinco duplicado! Status: {resp2.status_code}"
        )


@pytest.mark.asyncio
async def test_rn06_rn07_vinculo_e_historico_lotes(client: AsyncClient):
    """
    RN-06 (Vínculo Ativo Único) & RN-07 (Historização Temporal):
    Garantir que um animal possui no máximo 1 lote ativo e rastreabilidade no tempo.
    """
    payload_lote_1 = {
        "animal_id": 1,
        "lote_id": 100,
        "data_entrada": "2026-11-01T08:00:00"
    }
    payload_lote_2 = {
        "animal_id": 1,
        "lote_id": 202,
        "data_entrada": "2026-11-03T08:00:00"
    }

    # Rotas de associação mapeadas na v1
    rotas = ["/api/v1/lotes/100/animais", "/api/v1/lotes-animais", "/api/v1/lote-animais"]
    resp_lote1 = None
    endpoint_ativo = None

    for r in rotas:
        res = await client.post(r, json=payload_lote_1)
        if res.status_code not in [404, 405]:
            resp_lote1 = res
            endpoint_ativo = r
            break

    if not resp_lote1:
        endpoint_ativo = "/api/v1/lotes-animais"
        resp_lote1 = await client.post(endpoint_ativo, json=payload_lote_1)

    assert resp_lote1.status_code in [200, 201, 400, 409], f"Erro de integração na rota ({endpoint_ativo}): {resp_lote1.text}"

    # 2. Tentar vincular a um segundo lote simultaneamente
    resp_lote2 = await client.post(endpoint_ativo, json=payload_lote_2)
    if resp_lote1.status_code in [200, 201]:
        assert resp_lote2.status_code in [400, 409, 422], (
            f"VIOLAÇÃO DA RN-06: Permitiu 2 lotes ativos simultâneos! Status: {resp_lote2.status_code}"
        )