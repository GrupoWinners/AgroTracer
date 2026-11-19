from datetime import date, timedelta

import pytest
from sqlalchemy import event

from app.models.manejo_nutricional import ManejoNutricional
from test_s2_t01_api import ambiente_api  # noqa: F401
from test_s4_t02_fechamento import fechamento_api, enviar  # noqa: F401


@pytest.mark.parametrize("quantidade", [1, 20])
def test_consulta_fatores_nao_cresce_por_manejo(request, quantidade):
    cenario = request.getfixturevalue("fechamento_api")
    _, sessao, ids = cenario
    with sessao() as db:
        for numero in range(1, quantidade):
            dia = date(2026, 2, 1) + timedelta(days=numero)
            db.add(ManejoNutricional(
                lote_id=ids["lote"], parametro_set_id=ids["parametros"],
                inicio=dia, fim=dia, tipo_dieta="PASTAGEM",
            ))
        db.commit()
        engine = db.get_bind()
    consultas = []

    def contar(conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith("SELECT"):
            consultas.append(statement)

    event.listen(engine, "before_cursor_execute", contar)
    try:
        resposta = enviar(cenario, data_abate="2026-03-01")
        assert resposta.status_code == 201, resposta.text
    finally:
        event.remove(engine, "before_cursor_execute", contar)
    fatores = sum("FROM fatores" in sql for sql in consultas)
    assert fatores == 1, {"manejos": quantidade, "consultas_fatores": fatores}
