import pytest
from sqlalchemy import func, select

from app.models.certificado import Certificado
from app.models.fechamento_lote import FechamentoLote
from app.models.lote import Lote
from app.models.snapshot_fechamento import SnapshotFechamento
from app.models.token_publico import TokenPublico
from app.services.certificacao_service import conteudo_snapshot, sha256_json
from app.services.token_service import hash_token
from test_s2_t01_api import ambiente_api  # noqa: F401
from test_s4_t02_fechamento import fechamento_api, enviar  # noqa: F401


def emitir(cenario, chave="teste-1", lote_id=None, **alteracoes):
    cliente, _, ids = cenario
    return cliente.post(
        f'/api/v1/lotes/{lote_id or ids["lote"]}/certificar',
        headers={"Idempotency-Key": chave} if chave is not None else {},
        json={
            "data_abate": "2026-02-02", "numero_animais_abate": 1,
            "peso_medio_abate_kg": "540", "rendimento_carcaca": "0.53",
            **alteracoes,
        },
    )


def test_emissao_atomica_e_hash(request):
    cenario = request.getfixturevalue("fechamento_api")
    resposta = emitir(cenario)
    assert resposta.status_code == 201, resposta.text
    assert resposta.headers["cache-control"] == "no-store"
    corpo = resposta.json()
    with cenario[1]() as db:
        cert = db.get(Certificado, corpo["id"])
        snap = db.get(SnapshotFechamento, cert.snapshot_id)
        assert cert.snapshot_sha256 == sha256_json(conteudo_snapshot(snap))
        assert db.get(TokenPublico, cert.token_id).token_hash == hash_token(
            corpo["token"],
        )
        assert db.get(Lote, cenario[2]["lote"]).status == "FECHADO"


def test_repeticao_chaves_e_payload(request):
    cenario = request.getfixturevalue("fechamento_api")
    assert emitir(cenario).status_code == 201
    for chave, dados, codigo in [
        ("teste-1", {}, "CERTIFICACAO_JA_PROCESSADA"),
        ("teste-1", {"peso_medio_abate_kg": "600"},
         "IDEMPOTENCY_KEY_REUTILIZADA"),
        ("outra", {}, "CERTIFICADO_JA_EXISTENTE"),
    ]:
        resposta = emitir(cenario, chave, **dados)
        assert resposta.status_code == 409
        assert resposta.json()["error"]["code"] == codigo
        assert "token" not in resposta.json()
    with cenario[1]() as db:
        assert db.scalar(select(func.count(Certificado.id))) == 1
        assert db.scalar(select(func.count(TokenPublico.id))) == 1


@pytest.mark.parametrize("etapa", [
    "app.services.fechamento_service.calcular_emissoes",
    "app.services.fechamento_service.persistir_snapshot_fechamento",
    "app.services.certificacao_service.emitir_token",
    "app.services.certificacao_service.registrar_auditoria",
])
def test_rollback_integral(request, monkeypatch, etapa):
    cenario = request.getfixturevalue("fechamento_api")

    def falha(*args, **kwargs):
        raise RuntimeError("falha injetada")

    monkeypatch.setattr(etapa, falha)
    with pytest.raises(RuntimeError, match="falha injetada"):
        emitir(cenario)
    with cenario[1]() as db:
        assert db.get(Lote, cenario[2]["lote"]).status == "EM_MANEJO"
        for modelo in (
            Certificado, TokenPublico, FechamentoLote, SnapshotFechamento,
        ):
            assert db.scalar(select(func.count(modelo.id))) == 0


def test_fechado_sprint4_reutiliza_snapshot(request):
    cenario = request.getfixturevalue("fechamento_api")
    assert enviar(cenario).status_code == 201
    assert emitir(cenario, peso_medio_abate_kg="600").status_code == 409
    assert emitir(cenario).status_code == 201
    with cenario[1]() as db:
        assert db.scalar(select(func.count(SnapshotFechamento.id))) == 1


@pytest.mark.parametrize("chave", [None, "", " ", "a" * 129])
def test_chave_obrigatoria(request, chave):
    cenario = request.getfixturevalue("fechamento_api")
    assert emitir(cenario, chave).status_code == 422


def test_nao_autorizado_e_inexistente_mesma_resposta(request):
    cenario = request.getfixturevalue("fechamento_api")
    from app.core.bridge_dependency import exigir_usuario_wordpress
    from app.main import app
    app.dependency_overrides[exigir_usuario_wordpress] = lambda: 999
    outra = emitir(cenario)
    ausente = emitir(cenario, lote_id=99999)
    assert outra.status_code == ausente.status_code == 404
    assert outra.json()["error"]["code"] == ausente.json()["error"]["code"]
