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
async def test_rn06_vinculo_unico_e_desassociacao_lote(client: AsyncClient):
    """
    RN-06: Vínculo temporal ativo único por lote.
    - Um animal não pode estar em dois lotes ativos simultaneamente.
    - Desassociação encerra o vínculo ativo.
    """
    sufixo = str(uuid.uuid4())[:8]

    # 1. Criar Fazenda preparatória
    payload_fazenda = {"nome": f"Fazenda QA {sufixo}", "municipio": "Araguari", "uf": "MG"}
    resp_fazenda = await client.post("/api/v1/fazendas", json=payload_fazenda)
    fazenda_id = resp_fazenda.json().get("id") or (resp_fazenda.json().get("data", {}) or {}).get("id", 1) if resp_fazenda.status_code in [200, 201] else 1

    # 2. Criar Lote A e Lote B
    payload_lote_a = {"fazenda_id": fazenda_id, "codigo_lote": f"LOTE-A-{sufixo}"}
    payload_lote_b = {"fazenda_id": fazenda_id, "codigo_lote": f"LOTE-B-{sufixo}"}

    resp_la = await client.post("/api/v1/lotes", json=payload_lote_a)
    lote_a_id = resp_la.json().get("id") or (resp_la.json().get("data", {}) or {}).get("id")

    resp_lb = await client.post("/api/v1/lotes", json=payload_lote_b)
    lote_b_id = resp_lb.json().get("id") or (resp_lb.json().get("data", {}) or {}).get("id")

    # 3. Criar Animal
    payload_animal = {"identificador": f"BR-RN06-{sufixo}", "rfid": f"RFID-RN06-{sufixo}"}
    resp_animal = await client.post("/api/v1/animais", json=payload_animal)
    animal_id = resp_animal.json().get("id") or (resp_animal.json().get("data", {}) or {}).get("id")

    # 4. Associar ao Lote A (Primeiro vínculo ativo)
    resp_assoc1 = await client.post(f"/api/v1/lotes/{lote_a_id}/animais", json={"animal_id": animal_id})
    assert resp_assoc1.status_code in [200, 201], f"Erro na primeira associação: {resp_assoc1.text}"

    # 5. Tentativa de associar a outro lote ativo simultâneo (Lote B) -> DEVE dar 409 Conflict
    resp_assoc2 = await client.post(f"/api/v1/lotes/{lote_b_id}/animais", json={"animal_id": animal_id})
    assert resp_assoc2.status_code == 409, f"RN-06 VIOLADA: API permitiu 2 lotes ativos simultâneos! Status: {resp_assoc2.status_code}"

    # 6. Desassociação (Encerrar vínculo)
    resp_desassoc = await client.delete(f"/api/v1/lotes/{lote_a_id}/animais/{animal_id}")
    assert resp_desassoc.status_code in [200, 204], f"Falha ao desassociar animal do lote: {resp_desassoc.text}"


@pytest.mark.asyncio
async def test_rn07_validar_regras_xor_movimentacao(client: AsyncClient):
    """
    RN-07: Validação de Movimentações (Operador Lógico XOR e Origem/Destino).
    - Deve rejeitar se informar animal_id E lote_id simultaneamente no mesmo payload.
    - Deve rejeitar se NÃO informar nem animal_id nem lote_id.
    - Deve rejeitar se a origem for igual ao destino.
    """
    sufixo = str(uuid.uuid4())[:8]

    # 1. Preparar Fazenda e Lotes
    payload_fazenda = {"nome": f"Fazenda QA Mov {sufixo}", "municipio": "Araguari", "uf": "MG"}
    resp_fazenda = await client.post("/api/v1/fazendas", json=payload_fazenda)
    fazenda_id = resp_fazenda.json().get("id") or (resp_fazenda.json().get("data", {}) or {}).get("id", 1) if resp_fazenda.status_code in [200, 201] else 1

    resp_la = await client.post("/api/v1/lotes", json={"fazenda_id": fazenda_id, "codigo_lote": f"MOV-A-{sufixo}"})
    lote_a_id = resp_la.json().get("id") or (resp_la.json().get("data", {}) or {}).get("id")

    resp_lb = await client.post("/api/v1/lotes", json={"fazenda_id": fazenda_id, "codigo_lote": f"MOV-B-{sufixo}"})
    lote_b_id = resp_lb.json().get("id") or (resp_lb.json().get("data", {}) or {}).get("id")

    resp_animal = await client.post("/api/v1/animais", json={"identificador": f"BR-MOV-{sufixo}", "rfid": f"RFID-MOV-{sufixo}"})
    animal_id = resp_animal.json().get("id") or (resp_animal.json().get("data", {}) or {}).get("id")

    # CENÁRIO 1 (RN-07 XOR VIOLADO): Enviar AMBOS (animal_id E lote_id) -> DEVE dar 400 ou 422
    payload_ambos = {
        "animal_id": animal_id,
        "lote_id": lote_a_id,
        "lote_origem_id": lote_a_id,
        "lote_destino_id": lote_b_id
    }
    resp_ambos = await client.post("/api/v1/movimentacoes", json=payload_ambos)
    assert resp_ambos.status_code in [400, 422], f"RN-07 VIOLADA: API aceitou animal_id E lote_id juntos! Status: {resp_ambos.status_code}"

    # CENÁRIO 2 (RN-07 XOR VIOLADO): Enviar NENHUM (sem animal_id e sem lote_id) -> DEVE dar 400 ou 422
    payload_nenhum = {
        "lote_origem_id": lote_a_id,
        "lote_destino_id": lote_b_id
    }
    resp_nenhum = await client.post("/api/v1/movimentacoes", json=payload_nenhum)
    assert resp_nenhum.status_code in [400, 422], f"RN-07 VIOLADA: API aceitou payload sem animal_id e sem lote_id! Status: {resp_nenhum.status_code}"

    # CENÁRIO 3 (RN-07 ORIGEM=DESTINO): Origem igual ao Destino -> DEVE dar 400 ou 422
    payload_origem_destino_iguais = {
        "animal_id": animal_id,
        "lote_origem_id": lote_a_id,
        "lote_destino_id": lote_a_id
    }
    resp_iguais = await client.post("/api/v1/movimentacoes", json=payload_origem_destino_iguais)
    assert resp_iguais.status_code in [400, 422], f"RN-07 VIOLADA: API aceitou movimentação com origem igual ao destino! Status: {resp_iguais.status_code}"