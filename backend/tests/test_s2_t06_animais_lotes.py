import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_rn05_impedir_duplicidade_brinco_animal(client: AsyncClient):
    """
    RN-05: Validacao da unicidade do identificador do animal.
    Rejeita cadastro duplicado com 409 Conflict.
    """
    sufixo_unico = str(uuid.uuid4())[:8]
    identificador_teste = f"BR-2026-{sufixo_unico}"

    payload_animal = {
        "identificador": identificador_teste,
        "rfid": f"RFID-{sufixo_unico}"
    }

    # 1. Primeiro cadastro
    resp1 = await client.post("/api/v1/animais", json=payload_animal)
    assert resp1.status_code in [200, 201], (
        f"Erro no primeiro cadastro: {resp1.text}"
    )

    # 2. Segundo cadastro com o mesmo identificador (DEVE ser 409 Conflict)
    resp2 = await client.post("/api/v1/animais", json=payload_animal)
    assert resp2.status_code == 409, (
        f"RN-05 VIOLADA: API permitiu identificador duplicado! "
        f"Status: {resp2.status_code}"
    )
    assert (
        "ANIMAL_IDENTIFICADOR_DUPLICADO" in resp2.text
        or "ja existe" in resp2.text.lower()
        or "já existe" in resp2.text.lower()
    )


@pytest.mark.asyncio
async def test_rn06_vinculo_unico_e_desassociacao_lote(client: AsyncClient):
    """
    RN-06: Vinculo temporal ativo unico por lote.
    - Um animal nao pode estar em dois lotes ativos simultaneamente.
    - Desassociacao encerra o vinculo ativo.
    """
    sufixo = str(uuid.uuid4())[:8]

    # 1. Criar Fazenda preparatoria
    payload_fazenda = {
        "nome": f"Fazenda QA {sufixo}",
        "municipio": "Araguari",
        "uf": "MG"
    }
    resp_fazenda = await client.post("/api/v1/fazendas", json=payload_fazenda)
    if resp_fazenda.status_code in [200, 201]:
        data_f = resp_fazenda.json()
        fazenda_id = (
            data_f.get("id") or (data_f.get("data") or {}).get("id", 1)
        )
    else:
        fazenda_id = 1

    # 2. Criar Lote A e Lote B
    payload_lote_a = {
        "fazenda_id": fazenda_id,
        "codigo_lote": f"LOTE-A-{sufixo}"
    }
    payload_lote_b = {
        "fazenda_id": fazenda_id,
        "codigo_lote": f"LOTE-B-{sufixo}"
    }

    resp_la = await client.post("/api/v1/lotes", json=payload_lote_a)
    data_la = resp_la.json()
    lote_a_id = data_la.get("id") or (data_la.get("data") or {}).get("id")

    resp_lb = await client.post("/api/v1/lotes", json=payload_lote_b)
    data_lb = resp_lb.json()
    lote_b_id = data_lb.get("id") or (data_lb.get("data") or {}).get("id")

    # 3. Criar Animal
    payload_animal = {
        "identificador": f"BR-RN06-{sufixo}",
        "rfid": f"RFID-RN06-{sufixo}"
    }
    resp_animal = await client.post("/api/v1/animais", json=payload_animal)
    data_an = resp_animal.json()
    animal_id = data_an.get("id") or (data_an.get("data") or {}).get("id")

    # 4. Associar ao Lote A (Primeiro vinculo ativo)
    resp_assoc1 = await client.post(
        f"/api/v1/lotes/{lote_a_id}/animais",
        json={"animal_id": animal_id}
    )
    assert resp_assoc1.status_code in [200, 201], (
        f"Erro na primeira associacao: {resp_assoc1.text}"
    )

    # 5. Tentativa de associar a outro lote ativo simultaneo -> 409 Conflict
    resp_assoc2 = await client.post(
        f"/api/v1/lotes/{lote_b_id}/animais",
        json={"animal_id": animal_id}
    )
    assert resp_assoc2.status_code == 409, (
        f"RN-06 VIOLADA: API permitiu 2 lotes ativos simultaneos! "
        f"Status: {resp_assoc2.status_code}"
    )

    # 6. Desassociacao (Encerrar vinculo)
    resp_desassoc = await client.delete(
        f"/api/v1/lotes/{lote_a_id}/animais/{animal_id}"
    )
    assert resp_desassoc.status_code in [200, 204], (
        f"Falha ao desassociar animal do lote: {resp_desassoc.text}"
    )


@pytest.mark.asyncio
async def test_rn07_validar_regras_xor_movimentacao(client: AsyncClient):
    """
    RN-07: Validacao de Movimentacoes (Operador Logico XOR e Origem/Destino).
    - Deve rejeitar se informar animal_id E lote_id simultaneamente.
    - Deve rejeitar se NAO informar nem animal_id nem lote_id.
    - Deve rejeitar se a origem for igual ao destino.
    """
    sufixo = str(uuid.uuid4())[:8]

    # 1. Preparar Fazenda e Lotes
    payload_fazenda = {
        "nome": f"Fazenda QA Mov {sufixo}",
        "municipio": "Araguari",
        "uf": "MG"
    }
    resp_fazenda = await client.post("/api/v1/fazendas", json=payload_fazenda)
    if resp_fazenda.status_code in [200, 201]:
        data_f = resp_fazenda.json()
        fazenda_id = (
            data_f.get("id") or (data_f.get("data") or {}).get("id", 1)
        )
    else:
        fazenda_id = 1

    resp_la = await client.post(
        "/api/v1/lotes",
        json={"fazenda_id": fazenda_id, "codigo_lote": f"MOV-A-{sufixo}"}
    )
    data_la = resp_la.json()
    lote_a_id = data_la.get("id") or (data_la.get("data") or {}).get("id")

    resp_lb = await client.post(
        "/api/v1/lotes",
        json={"fazenda_id": fazenda_id, "codigo_lote": f"MOV-B-{sufixo}"}
    )
    data_lb = resp_lb.json()
    lote_b_id = data_lb.get("id") or (data_lb.get("data") or {}).get("id")

    resp_animal = await client.post(
        "/api/v1/animais",
        json={
            "identificador": f"BR-MOV-{sufixo}",
            "rfid": f"RFID-MOV-{sufixo}"
        }
    )
    data_an = resp_animal.json()
    animal_id = data_an.get("id") or (data_an.get("data") or {}).get("id")

    # CENARIO 1 (RN-07 XOR VIOLADO): Enviar AMBOS (animal_id E lote_id)
    payload_ambos = {
        "animal_id": animal_id,
        "lote_id": lote_a_id,
        "lote_origem_id": lote_a_id,
        "lote_destino_id": lote_b_id
    }
    resp_ambos = await client.post("/api/v1/movimentacoes", json=payload_ambos)
    assert resp_ambos.status_code in [400, 422], (
        f"RN-07 VIOLADA: API aceitou animal_id E lote_id juntos! "
        f"Status: {resp_ambos.status_code}"
    )

    # CENARIO 2 (RN-07 XOR VIOLADO): Enviar NENHUM
    payload_nenhum = {
        "lote_origem_id": lote_a_id,
        "lote_destino_id": lote_b_id
    }
    resp_nenhum = await client.post(
        "/api/v1/movimentacoes",
        json=payload_nenhum
    )
    assert resp_nenhum.status_code in [400, 422], (
        f"RN-07 VIOLADA: API aceitou payload sem animal_id e sem lote_id! "
        f"Status: {resp_nenhum.status_code}"
    )

    # CENARIO 3 (RN-07 ORIGEM=DESTINO): Origem igual ao Destino
    payload_origem_destino_iguais = {
        "animal_id": animal_id,
        "lote_origem_id": lote_a_id,
        "lote_destino_id": lote_a_id
    }
    resp_iguais = await client.post(
        "/api/v1/movimentacoes",
        json=payload_origem_destino_iguais
    )
    assert resp_iguais.status_code in [400, 422], (
        f"RN-07 VIOLADA: API aceitou movimentacao com origem igual ao "
        f"destino! Status: {resp_iguais.status_code}"
    )
