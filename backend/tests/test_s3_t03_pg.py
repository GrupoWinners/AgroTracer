"""POST concorrente e auditoria usando sessões PostgreSQL independentes."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from fastapi.testclient import TestClient
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.bridge_dependency import exigir_usuario_wordpress
from app.db.database import obter_db
from app.main import app
from app.models.auditoria_evento import AuditoriaEvento
from app.models.produtor import Produtor

from test_s3_t01_db import cenario_pg  # noqa: F401


def test_post_concorrente_e_auditoria_atomica(request):
    engine, ids = request.getfixturevalue("cenario_pg")
    with Session(engine) as db:
        wp_id = db.get(Produtor, ids[3]).wordpress_user_id

    def obter_db_teste():
        with Session(engine) as db:
            yield db

    overrides = app.dependency_overrides.copy()
    app.dependency_overrides[obter_db] = obter_db_teste
    app.dependency_overrides[exigir_usuario_wordpress] = lambda: wp_id
    barreira = Barrier(2)

    def enviar():
        cliente = TestClient(app)
        barreira.wait(timeout=10)
        return cliente.post(f"/api/v1/lotes/{ids[0]}/manejos", json={
            "inicio": "2026-11-01", "fim": "2026-11-10",
            "tipo_dieta": "PASTAGEM", "parametro_set_id": ids[1],
        })

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            futuros = [executor.submit(enviar) for _ in range(2)]
            respostas = [f.result(timeout=15) for f in futuros]
        assert sorted(r.status_code for r in respostas) == [201, 409]
        sucesso = next(r for r in respostas if r.status_code == 201)
        conflito = next(r for r in respostas if r.status_code == 409)
        assert conflito.json()["error"]["code"] == "MANEJO_SOBREPOSTO"
        with Session(engine) as db:
            eventos = db.scalars(select(AuditoriaEvento).where(
                AuditoriaEvento.wordpress_user_id == wp_id,
                AuditoriaEvento.acao == "CRIAR_MANEJO",
            )).all()
            assert len(eventos) == 1
            assert eventos[0].entidade_id == sucesso.json()["id"]
            assert eventos[0].correlation_id == (
                sucesso.headers["X-Correlation-ID"]
            )
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(overrides)
        with Session(engine) as db:
            db.execute(delete(AuditoriaEvento).where(
                AuditoriaEvento.wordpress_user_id == wp_id,
                AuditoriaEvento.acao == "CRIAR_MANEJO",
            ))
            db.commit()
