"""S3-T05: Testes de integracao da RN-08 (Manejo Nutricional).

Valida vigencias inclusivas, rejeicao de fim < inicio e sobreposicao.
"""
from datetime import date, timedelta

from test_s2_t01_api import ambiente_api  # noqa: F401
from test_s2_t03_api import cenario  # noqa: F401
from test_s3_t03_api import enviar, manejo_api  # noqa: F401


def test_rn08_manejo_mesmo_dia_conta_um_dia(manejo_api):  # noqa: F811
    """RN-08: Inicio igual a fim aceito e contabiliza 1 dia."""
    cliente, _, ids = manejo_api
    data_hoje = str(date.today())

    resposta = enviar(cliente, ids, inicio=data_hoje, fim=data_hoje)
    msg_erro = f"Erro ao criar manejo: {resposta.text}"
    assert resposta.status_code in [200, 201], msg_erro
    dados = resposta.json()
    assert dados["inicio"] == data_hoje
    assert dados["fim"] == data_hoje


def test_rn08_impedir_data_fim_anterior_a_inicio(manejo_api):  # noqa: F811
    """RN-08: Fim anterior ao inicio rejeitado com 400 ou 422."""
    cliente, _, ids = manejo_api
    data_inicio = str(date.today())
    data_fim = str(date.today() - timedelta(days=5))

    resposta = enviar(cliente, ids, inicio=data_inicio, fim=data_fim)
    msg_erro = (
        f"RN-08 VIOLADA: API aceitou fim < inicio! "
        f"Status: {resposta.status_code}"
    )
    assert resposta.status_code in [400, 422], msg_erro


def test_rn08_impedir_sobreposicao_de_periodos(manejo_api):  # noqa: F811
    """RN-08: Rejeitar novos manejos sobrepostos no mesmo lote."""
    cliente, _, ids = manejo_api

    # 1. Registrar manejo base
    d_inicio_1 = str(date.today() + timedelta(days=10))
    d_fim_1 = str(date.today() + timedelta(days=20))

    resp1 = enviar(cliente, ids, inicio=d_inicio_1, fim=d_fim_1)
    msg_erro1 = f"Erro ao registrar manejo base: {resp1.text}"
    assert resp1.status_code in [200, 201], msg_erro1

    # 2. Tentar registrar manejo sobreposto
    d_inicio_2 = str(date.today() + timedelta(days=15))
    d_fim_2 = str(date.today() + timedelta(days=25))

    resp2 = enviar(cliente, ids, inicio=d_inicio_2, fim=d_fim_2)
    msg_erro2 = (
        f"RN-08 VIOLADA: API permitiu sobreposicao! "
        f"Status: {resp2.status_code}"
    )
    assert resp2.status_code == 409, msg_erro2
    assert resp2.json()["error"]["code"] == "MANEJO_SOBREPOSTO"
