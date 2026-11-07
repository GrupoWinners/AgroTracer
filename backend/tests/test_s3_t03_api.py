import json
import time
from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import func, select

from app.core.bridge_dependency import exigir_usuario_wordpress
from app.core.hmac_protocol import build_canonical_string, gerar_assinatura
from app.main import app
from app.models.auditoria_evento import AuditoriaEvento
from app.models.fator import Fator
from app.models.manejo_nutricional import ManejoNutricional
from app.models.parametro_set import ParametroSet

from test_s2_t03_api import cenario  # noqa: F401
from test_s2_t01_api import ambiente_api  # noqa: F401


@pytest.fixture
def manejo_api(request, monkeypatch):
    cliente, sessao, ids = request.getfixturevalue("cenario")
    monkeypatch.setenv("AGROTRACER_ADMIN_WP_IDS", "42")
    demo = json.loads((Path(__file__).parents[1] / "examples" /
                       "parametros_demo.json").read_text(encoding="utf-8"))
    with sessao() as db:
        conjunto = ParametroSet(
            versao=demo["versao"],
            vigencia_inicio=date.fromisoformat(demo["vigencia_inicio"]),
        )
        db.add(conjunto)
        db.flush()
        for fator in demo["fatores"]:
            db.add(Fator(
                parametro_set_id=conjunto.id,
                **dict(fator, valor=Decimal(fator["valor"])),
            ))
        ids["parametro"] = conjunto.id
        db.commit()
    return cliente, sessao, ids


def payload(ids, **alteracoes):
    return {
        "inicio": "2026-11-01", "fim": "2026-11-10",
        "tipo_dieta": "PASTAGEM", "parametro_set_id": ids["parametro"],
        **alteracoes,
    }


def enviar(cliente, ids, **alteracoes):
    return cliente.post(
        f'/api/v1/lotes/{ids["lote"]}/manejos',
        json=payload(ids, **alteracoes),
    )


def test_criar_manejo_auditoria_e_correlation_id(manejo_api):
    cliente, sessao, ids = manejo_api
    correlation = str(uuid4())
    resposta = cliente.post(
        f'/api/v1/lotes/{ids["lote"]}/manejos', json=payload(ids),
        headers={"X-Correlation-ID": correlation},
    )
    assert resposta.status_code == 201, resposta.text
    assert resposta.headers["X-Correlation-ID"] == correlation
    with sessao() as db:
        evento = db.scalar(select(AuditoriaEvento).where(
            AuditoriaEvento.acao == "CRIAR_MANEJO"
        ))
        assert evento.entidade_id == resposta.json()["id"]
        assert evento.wordpress_user_id == 42
        assert evento.correlation_id == correlation
        assert evento.detalhes["parametro_set_id"] == ids["parametro"]


def test_sobreposicao_409_e_dia_seguinte(manejo_api):
    cliente, sessao, ids = manejo_api
    assert enviar(cliente, ids).status_code == 201
    resposta = enviar(cliente, ids, inicio="2026-11-10")
    assert resposta.status_code == 409
    assert resposta.json()["error"]["code"] == "MANEJO_SOBREPOSTO"
    assert resposta.json()["error"]["correlation_id"] == (
        resposta.headers["X-Correlation-ID"]
    )
    assert enviar(cliente, ids, inicio="2026-11-11",
                  fim="2026-11-11").status_code == 201
    with sessao() as db:
        assert db.scalar(select(func.count()).select_from(
            ManejoNutricional
        )) == 2


@pytest.mark.parametrize("alteracoes", [
    {"fim": "2026-10-31"}, {"inicio": "2026-02-30"},
    {"inicio": 1793491200}, {"tipo_dieta": " "},
    {"tipo_dieta": "x" * 51}, {"parametro_set_id": 0},
    {"parametro_set_id": True}, {"wordpress_user_id": 84},
])
def test_422_sem_gravacao(manejo_api, alteracoes):
    cliente, sessao, ids = manejo_api
    resposta = enviar(cliente, ids, **alteracoes)
    assert resposta.status_code == 422
    assert resposta.json()["error"]["correlation_id"] == (
        resposta.headers["X-Correlation-ID"]
    )
    with sessao() as db:
        assert db.scalar(select(func.count()).select_from(
            ManejoNutricional
        )) == 0


def test_autorizacao_objeto_e_recurso_ausente(manejo_api):
    cliente, sessao, ids = manejo_api
    respostas = []
    for lote_id in [ids["lote_outro"], 999999]:
        resposta = cliente.post(
            f"/api/v1/lotes/{lote_id}/manejos", json=payload(ids)
        )
        assert resposta.status_code == 404
        respostas.append(resposta.json()["error"]["message"])
    assert respostas[0] == respostas[1]
    assert enviar(cliente, ids, parametro_set_id=999999).status_code == 404


def test_falha_auditoria_desfaz_manejo(manejo_api, monkeypatch):
    cliente, sessao, ids = manejo_api

    def falhar(**kwargs):
        raise RuntimeError("Falha simulada de auditoria")

    monkeypatch.setattr(
        "app.api.v1.manejos.registrar_auditoria", falhar
    )
    with pytest.raises(RuntimeError, match="Falha simulada"):
        enviar(cliente, ids)
    with sessao() as db:
        assert db.scalar(select(func.count()).select_from(
            ManejoNutricional
        )) == 0


def test_lista_parametros_admin_fonte_decimal_filtro(manejo_api):
    cliente, _, ids = manejo_api
    path = "/api/v1/admin/parametro-sets"
    resposta = cliente.get(path + "?status=RASCUNHO&limit=1")
    assert resposta.status_code == 200
    assert resposta.json()[0]["id"] == ids["parametro"]
    fator = resposta.json()[0]["fatores"][0]
    assert Decimal(fator["valor"]) == Decimal("2.10")
    assert isinstance(fator["valor"], str)
    assert fator["source_type"] == "SYNTHETIC"
    assert fator["source_uri"] is None
    assert cliente.get(path + "?status=ATIVO").json() == []
    assert cliente.get(path + "?offset=1").json() == []
    assert cliente.get(path + "?limit=101").status_code == 422
    assert cliente.get(path + "?status=ERRADO").status_code == 422
    app.dependency_overrides[exigir_usuario_wordpress] = lambda: 84
    assert cliente.get(path).status_code == 403


def assinar(method, path, corpo, user_id=42):
    timestamp = int(time.time())
    nonce = uuid4().hex
    chave = b"segredo_ficticio_exclusivamente_para_testes"
    canonical = build_canonical_string(
        method=method, path_with_query=path, timestamp=timestamp,
        nonce=nonce, wp_user_id=user_id, body=corpo,
    )
    return {
        "Content-Type": "application/json",
        "X-Correlation-ID": str(uuid4()),
        "X-AgroTracer-Signature": gerar_assinatura(canonical, chave),
        "X-AgroTracer-Timestamp": str(timestamp),
        "X-AgroTracer-Nonce": nonce,
        "X-AgroTracer-User-Id": str(user_id),
    }


@pytest.mark.parametrize("method", ["POST", "GET"])
def test_hmac_real_nas_rotas(manejo_api, monkeypatch, method):
    cliente, _, ids = manejo_api
    monkeypatch.setenv("AGROTRACER_BRIDGE_SECRET",
                       "segredo_ficticio_exclusivamente_para_testes")
    app.dependency_overrides.pop(exigir_usuario_wordpress)
    app.state.redis_cliente.set.return_value = True
    path = (f'/api/v1/lotes/{ids["lote"]}/manejos' if method == "POST"
            else "/api/v1/admin/parametro-sets")
    corpo = json.dumps(payload(ids)).encode() if method == "POST" else b""
    assert cliente.request(method, path, content=corpo).status_code == 401
    headers = assinar(method, path, corpo)
    adulterados = dict(headers, **{"X-AgroTracer-User-Id": "84"})
    assert cliente.request(method, path, content=corpo,
                           headers=adulterados).status_code == 401
    resposta = cliente.request(method, path, content=corpo, headers=headers)
    assert resposta.status_code == (201 if method == "POST" else 200)
    app.state.redis_cliente.set.return_value = False
    assert cliente.request(method, path, content=corpo,
                           headers=headers).status_code == 401


def test_openapi_contratos():
    paths = app.openapi()["paths"]
    post = paths["/api/v1/lotes/{lote_id}/manejos"]["post"]
    assert {"201", "401", "403", "404", "409", "422"} <= set(
        post["responses"]
    )
    assert "MANEJO_SOBREPOSTO" in post["responses"]["409"]["description"]
    assert "get" in paths["/api/v1/admin/parametro-sets"]
    assert post["responses"]["422"]["content"]["application/json"][
        "schema"
    ]["$ref"].endswith("/ErrorResponse")
    headers = {p["name"] for p in post["parameters"] if p["in"] == "header"}
    assert {"X-AgroTracer-Signature", "X-Correlation-ID"} <= headers
