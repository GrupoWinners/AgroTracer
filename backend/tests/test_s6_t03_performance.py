"""Benchmark reproduzivel sem alegar carga/latencia de producao."""

import json
import math
import os
import platform
from pathlib import Path
from time import perf_counter
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, delete, inspect, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateSchema, DropSchema

from app.db.database import obter_db
from app.main import app
from app.models import Base
from app.models.certificado_pdf import CertificadoPDF
from test_s2_t01_api import ambiente_api  # noqa: F401
from test_s4_t02_fechamento import fechamento_api  # noqa: F401
from test_s5_t01_certificacao import emitir


@pytest.fixture
def medicao(request):
    cenario = request.getfixturevalue("fechamento_api")
    url = os.getenv("AGROTRACER_TEST_DATABASE_URL")
    if not url:
        yield cenario, "sqlite", {}
        return
    assert make_url(url).database == "agrotracer_s2_t01_teste"
    engine = create_engine(url)
    schema = "s6_performance_" + uuid4().hex
    isolado = engine.execution_options(schema_translate_map={None: schema})
    with engine.begin() as conn:
        conn.execute(CreateSchema(schema))
    fabrica = sessionmaker(bind=isolado)
    try:
        Base.metadata.create_all(isolado)
        with cenario[1]() as origem, isolado.begin() as destino:
            for tabela in Base.metadata.sorted_tables:
                registros = origem.execute(select(tabela)).mappings().all()
                if registros:
                    destino.execute(
                        tabela.insert(), [dict(r) for r in registros],
                    )
                    if "id" in tabela.c:
                        sequencia = destino.scalar(text(
                            "SELECT pg_get_serial_sequence(:tabela, 'id')"
                        ), {"tabela": f"{schema}.{tabela.name}"})
                        if sequencia:
                            destino.execute(text(
                                "SELECT setval(:seq, :valor, true)"
                            ), {"seq": sequencia, "valor": max(
                                r["id"] for r in registros
                            )})

        def obter_teste():
            with fabrica() as db:
                yield db

        app.dependency_overrides[obter_db] = obter_teste
        inspetor = inspect(engine)
        indices = {
            nome: [i["name"] for i in inspetor.get_indexes(nome)]
            for nome in ("fatores", "manejos_nutricionais", "certificados")
        }
        yield (cenario[0], fabrica, cenario[2]), "postgresql", indices
    finally:
        with engine.begin() as conn:
            conn.execute(DropSchema(schema, cascade=True))
        engine.dispose()


def test_registrar_p95_crud_pdf(medicao):
    cenario, banco, indices = medicao
    cliente, sessao, _ = cenario
    cert = emitir(cenario)
    assert cert.status_code == 201, cert.text
    cert_id = cert.json()["id"]
    medicoes = {}
    for operacao in ("criar_fazenda", "listar_fazendas", "editar_fazenda",
                     "pdf_gerar_persistir", "pdf_download"):
        tempos = []
        for numero in range(33):
            if operacao == "pdf_gerar_persistir":
                with sessao() as db:
                    db.execute(delete(CertificadoPDF).where(
                        CertificadoPDF.certificado_id == cert_id,
                    ))
                    db.commit()
            inicio = perf_counter()
            if operacao == "criar_fazenda":
                resp = cliente.post("/api/v1/fazendas", json={
                    "nome": f"SYNTHETIC-{numero}",
                    "municipio": "Teste", "uf": "MG",
                })
                fazenda_id = resp.json().get("id")
            elif operacao == "listar_fazendas":
                resp = cliente.get("/api/v1/fazendas")
            elif operacao == "editar_fazenda":
                resp = cliente.put(f"/api/v1/fazendas/{fazenda_id}", json={
                    "nome": f"SYNTHETIC-EDIT-{numero}",
                })
            else:
                resp = cliente.get(f"/api/v1/certificados/{cert_id}/pdf")
            tempo = (perf_counter() - inicio) * 1000
            assert resp.status_code in (200, 201), resp.text
            if numero >= 3:  # aquecimento excluido
                tempos.append(tempo)
        p95 = sorted(tempos)[math.ceil(len(tempos) * .95) - 1]
        meta = 3000 if operacao.startswith("pdf") else 800
        medicoes[operacao] = {
            "amostras_ms": [round(t, 3) for t in tempos],
            "p95_ms": round(p95, 3), "meta_ms": meta,
            "meta_atendida": p95 <= meta if meta == 3000 else p95 < meta,
        }
    relatorio = {
        "banco": banco, "python": platform.python_version(),
        "transporte": "ASGI TestClient; HMAC/Redis substituidos pela fixture",
        "carga": "1 cliente sequencial, 3 aquecimentos + 30 amostras",
        "dataset": "34 fazendas sinteticas, 1 lote/animal/manejo/certificado",
        "limites": (
            "Nao mede rede, proxy, WP, autenticacao nem carga simultanea"
        ),
        "indices_banco_migrado": indices, "medicoes": medicoes,
    }
    destino = os.getenv("AGROTRACER_PERF_REPORT")
    if destino:
        Path(destino).parent.mkdir(parents=True, exist_ok=True)
        Path(destino).write_text(
            json.dumps(relatorio, indent=2), encoding="utf-8",
        )
    print(json.dumps(relatorio))
