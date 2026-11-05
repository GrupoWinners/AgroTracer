import uuid
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_rn05_impedir_duplicidade_brinco_animal(client: AsyncClient):
    """
    RN-05: Validação da unicidade do identificador do animal.
    O cadastro de dois animais com o mesmo identificador deve ser rejeitado com 409 Conflict.
    """
    sufixo_unico = str(uuid.uuid4())[:8]
    identificador_teste = f"BR-2026-{sufixo_unico}"

    payload_animal = {
        "identificador": identificador_teste,
        "rfid": f"RFID-{sufixo_unico}"
    }

    # 1. Primeiro cadastro
    resp1 = await client.post("/api/v1/animais", json=payload_animal)
    assert resp1.status_code in [200, 201], f"Erro no primeiro cadastro: {resp1.text}"

    # 2. Segundo cadastro com o mesmo identificador (DEVE ser rejeitado com 409 Conflict)
    resp2 = await client.post("/api/v1/animais", json=payload_animal)
    assert resp2.status_code == 409, f"RN-05 VIOLADA: API permitiu identificador duplicado! Status: {resp2.status_code}"
    assert "ANIMAL_IDENTIFICADOR_DUPLICADO" in resp2.text or "já existe" in resp2.text.lower()


@pytest.mark.asyncio
async def test_rn06_rn07_vinculo_e_historico_lotes(client: AsyncClient):
    """
    RN-06 & RN-07: Vínculo temporal ativo único e desassociação/historização.
    - RN-06: Um animal não pode estar em dois lotes ativos ao mesmo tempo.
    - RN-07: O histórico cronológico e desassociação devem funcionar.
    """
    sufixo = str(uuid.uuid4())[:8]

    # 1. Cadastrar uma Fazenda preparatória para garantir que o fazenda_id exista no banco
    payload_fazenda = {
        "nome": f"Fazenda QA {sufixo}",
        "municipio": "Araguari",
        "uf": "MG"
    }
    resp_fazenda = await client.post("/api/v1/fazendas", json=payload_fazenda)
    
    # Extrai o fazenda_id se a criação for bem-sucedida, ou usa fallback
    if resp_fazenda.status_code in [200, 201]:
        json_fazenda = resp_fazenda.json()
        fazenda_id = json_fazenda.get("id") or (json_fazenda.get("data", {}) or {}).get("id", 1)
    else:
        fazenda_id = 1

    # 2. Criar Lote A e Lote B com a Fazenda Válida
    payload_lote_a = {"fazenda_id": fazenda_id, "codigo_lote": f"LOTE-A-{sufixo}"}
    payload_lote_b = {"fazenda_id": fazenda_id, "codigo_lote": f"LOTE-B-{sufixo}"}

    resp_la = await client.post("/api/v1/lotes", json=payload_lote_a)
    assert resp_la.status_code in [200, 201], f"Erro ao criar Lote A: {resp_la.text}"
    json_la = resp_la.json()
    lote_a_id = json_la.get("id") or (json_la.get("data", {}) or {}).get("id")

    resp_lb = await client.post("/api/v1/lotes", json=payload_lote_b)
    assert resp_lb.status_code in [200, 201], f"Erro ao criar Lote B: {resp_lb.text}"
    json_lb = resp_lb.json()
    lote_b_id = json_lb.get("id") or (json_lb.get("data", {}) or {}).get("id")

    # 3. Cadastrar Animal dinâmico para os testes de vínculo
    payload_animal = {
        "identificador": f"BR-VINC-{sufixo}",
        "rfid": f"RFID-VINC-{sufixo}"
    }
    resp_animal = await client.post("/api/v1/animais", json=payload_animal)
    assert resp_animal.status_code in [200, 201], f"Erro ao criar animal para vinculo: {resp_animal.text}"
    json_animal = resp_animal.json()
    animal_id = json_animal.get("id") or (json_animal.get("data", {}) or {}).get("id")

    # 4. RN-06: Associar ao primeiro Lote Ativo (Lote A)
    resp_assoc1 = await client.post(f"/api/v1/lotes/{lote_a_id}/animais", json={"animal_id": animal_id})
    assert resp_assoc1.status_code in [200, 201], f"Erro na primeira associação: {resp_assoc1.text}"

    # 5. RN-06: Tentativa de associar a outro lote ativo simultâneo (Lote B) -> DEVE dar 409 Conflict
    resp_assoc2 = await client.post(f"/api/v1/lotes/{lote_b_id}/animais", json={"animal_id": animal_id})
    assert resp_assoc2.status_code == 409, f"RN-06 VIOLADA: API permitiu 2 lotes ativos simultâneos! Status: {resp_assoc2.status_code}"

    # 6. RN-07: Desassociação temporal (Encerrar vínculo do Lote A)
    resp_desassoc = await client.delete(f"/api/v1/lotes/{lote_a_id}/animais/{animal_id}")
    assert resp_desassoc.status_code in [200, 204], f"RN-07 ERRO: Falha ao desassociar animal do lote: {resp_desassoc.text}"

    # 7. RN-07: Reassociar ao Lote B após encerrar o vínculo anterior
    resp_assoc3 = await client.post(f"/api/v1/lotes/{lote_b_id}/animais", json={"animal_id": animal_id})
    assert resp_assoc3.status_code in [200, 201], f"RN-07 ERRO: Falha ao reassociar após desassociação: {resp_assoc3.text}"