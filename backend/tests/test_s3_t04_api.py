from test_s2_t03_api import cenario  # noqa: F401
from test_s2_t01_api import ambiente_api  # noqa: F401
from test_s3_t03_api import manejo_api, payload, enviar  # noqa: F401


def test_listar_manejos_ordenados_cronologicamente(manejo_api):  # noqa: F811
    cliente, sessao, ids = manejo_api

    # 1. Lista inicialmente vazia
    res = cliente.get(f'/api/v1/lotes/{ids["lote"]}/manejos')
    assert res.status_code == 200
    assert res.json() == []

    # 2. Registra dois manejos válidos contíguos sem sobreposição
    r1 = enviar(cliente, ids, inicio="2026-11-01", fim="2026-11-10")
    assert r1.status_code == 201
    r2 = enviar(cliente, ids, inicio="2026-11-11", fim="2026-11-20")
    assert r2.status_code == 201

    # 3. Consulta lista e verifica ordenação cronológica
    res = cliente.get(f'/api/v1/lotes/{ids["lote"]}/manejos')
    assert res.status_code == 200
    itens = res.json()
    assert len(itens) == 2
    assert itens[0]["inicio"] == "2026-11-01"
    assert itens[0]["fim"] == "2026-11-10"
    assert itens[1]["inicio"] == "2026-11-11"
    assert itens[1]["fim"] == "2026-11-20"


def test_listar_manejos_autorizacao_por_objeto_idor(manejo_api):  # noqa: F811
    cliente, sessao, ids = manejo_api
    # Lote de outro produtor retorna 404
    res_outro = cliente.get(f'/api/v1/lotes/{ids["lote_outro"]}/manejos')
    assert res_outro.status_code == 404
    assert res_outro.json()["error"]["code"] == "LOTE_NAO_ENCONTRADO"

    # Lote inexistente retorna 404
    res_inexistente = cliente.get('/api/v1/lotes/999999/manejos')
    assert res_inexistente.status_code == 404
    assert res_inexistente.json()["error"]["code"] == "LOTE_NAO_ENCONTRADO"


def test_conflito_sobreposicao_identifica_periodo(manejo_api):  # noqa: F811
    cliente, sessao, ids = manejo_api
    r1 = enviar(cliente, ids, inicio="2026-11-01", fim="2026-11-10")
    assert r1.status_code == 201

    # Tentativa com sobreposição no dia 10
    r_conflito = enviar(cliente, ids, inicio="2026-11-10", fim="2026-11-15")
    assert r_conflito.status_code == 409
    erro = r_conflito.json()["error"]
    assert erro["code"] == "MANEJO_SOBREPOSTO"
    assert "detalhes" in erro
    assert erro["detalhes"]["inicio"] == "2026-11-01"
    assert erro["detalhes"]["fim"] == "2026-11-10"
    assert "2026-11-01" in erro["message"]
    assert "2026-11-10" in erro["message"]
