from decimal import Decimal
import time
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.bridge_dependency import exigir_usuario_wordpress
from app.db.database import obter_db
from app.main import app
from app.models import Base


# Setup compatibilidade de PostgreSQL DDL com SQLite em memoria
@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "TEXT"


engine_teste = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(engine_teste, "connect")
def configurar_funcoes_sqlite(dbapi_connection, connection_record):
    dbapi_connection.create_function(
        "btrim", 1, lambda s: s.strip() if s is not None else ""
    )
    dbapi_connection.create_function(
        "char_length", 1, lambda s: len(s) if s is not None else 0
    )


SessionTeste = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_teste,
)


@pytest.fixture(autouse=True)
def preparar_ambiente():
    Base.metadata.create_all(bind=engine_teste)
    app.state.redis_cliente = AsyncMock()
    yield
    Base.metadata.drop_all(bind=engine_teste)


def override_obter_db():
    db = SessionTeste()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[obter_db] = override_obter_db


@pytest.fixture
def cliente():
    with TestClient(app) as c:
        yield c


# ----------------------------------------------------------------------
# 1. MATRIZ DE CRUD (Produtor -> Fazenda -> Talhao) & BOLA
# ----------------------------------------------------------------------

def test_crud_fazenda_e_talhao_sucesso(cliente):
    app.dependency_overrides[exigir_usuario_wordpress] = lambda: 42

    # 1. Criar fazenda
    payload_fazenda = {
        "nome": "Fazenda Modelo",
        "municipio": "Aquidauana",
        "uf": "MS",
        "numero_car_informado": "MS-5401209-F38A89BC10D44A6890EF21AA4589CC10",
    }
    resp = cliente.post("/api/v1/fazendas", json=payload_fazenda)
    assert resp.status_code == 201
    fazenda_data = resp.json()
    assert fazenda_data["nome"] == "Fazenda Modelo"
    assert fazenda_data["uf"] == "MS"
    fazenda_id = fazenda_data["id"]

    # 2. Listar fazendas autorizadas
    resp = cliente.get("/api/v1/fazendas")
    assert resp.status_code == 200
    lista = resp.json()
    assert len(lista) == 1
    assert lista[0]["id"] == fazenda_id

    # 3. Criar talhao na fazenda
    payload_talhao = {
        "identificador": "Piquete 01",
        "area_hectares": "25.5000",
    }
    url_talhao = f"/api/v1/fazendas/{fazenda_id}/talhoes"
    resp = cliente.post(url_talhao, json=payload_talhao)
    assert resp.status_code == 201
    talhao_data = resp.json()
    assert talhao_data["identificador"] == "Piquete 01"
    assert Decimal(str(talhao_data["area_hectares"])) == Decimal("25.5000")

    # 4. Listar talhoes da fazenda
    resp = cliente.get(f"/api/v1/fazendas/{fazenda_id}/talhoes")
    assert resp.status_code == 200
    talhoes = resp.json()
    assert len(talhoes) == 1
    assert talhoes[0]["identificador"] == "Piquete 01"


def test_rejeita_car_duplicado_rn02(cliente):
    app.dependency_overrides[exigir_usuario_wordpress] = lambda: 42

    payload = {
        "nome": "Fazenda A",
        "municipio": "Miranda",
        "uf": "MS",
        "numero_car_informado": "CAR-UNICO-12345",
    }
    resp = cliente.post("/api/v1/fazendas", json=payload)
    assert resp.status_code == 201

    payload_duplicado = {
        "nome": "Fazenda B",
        "municipio": "Corumba",
        "uf": "MS",
        "numero_car_informado": "CAR-UNICO-12345",
    }
    resp_dup = cliente.post("/api/v1/fazendas", json=payload_duplicado)
    assert resp_dup.status_code == 409
    assert "cadastrado" in resp_dup.json()["detail"]


def test_autorizacao_por_objeto_bola(cliente):
    """Produtor B nao pode ver nem criar talhao na fazenda de A."""
    app.dependency_overrides[exigir_usuario_wordpress] = lambda: 100
    resp = cliente.post("/api/v1/fazendas", json={
        "nome": "Fazenda do Produtor 100",
        "municipio": "Bonito",
        "uf": "MS",
    })
    assert resp.status_code == 201
    fazenda_id = resp.json()["id"]

    app.dependency_overrides[exigir_usuario_wordpress] = lambda: 200
    resp_bola = cliente.get(f"/api/v1/fazendas/{fazenda_id}")
    assert resp_bola.status_code == 404

    url_talhao = f"/api/v1/fazendas/{fazenda_id}/talhoes"
    resp_bola_post = cliente.post(url_talhao, json={
        "identificador": "Invasao",
        "area_hectares": "10.0",
    })
    assert resp_bola_post.status_code == 404


# ----------------------------------------------------------------------
# 2. TESTES DE SEGURANCA DA BRIDGE (SEC-01 a SEC-04)
# ----------------------------------------------------------------------

def test_sec_01_hmac_tampering(cliente):
    """SEC-01: Rejeicao 401 quando assinatura HMAC for adulterada."""
    headers = {
        "X-AgroTracer-Key-Id": "wp-bridge-2026-01",
        "X-AgroTracer-Timestamp": str(int(time.time())),
        "X-AgroTracer-Nonce": "nonce-sec01-tampering",
        "X-AgroTracer-User-Id": "42",
        "X-AgroTracer-Signature": "sig_invalida_1234567890abcdef",
    }
    app.dependency_overrides.pop(exigir_usuario_wordpress, None)

    chave_mock = b"chave_secreta_segura_32_bytes_ok"
    with patch(
        "app.core.bridge_dependency.obter_chave_bridge",
        return_value=chave_mock,
    ), patch(
        "app.core.nonce_store.registrar_nonce",
        new_callable=AsyncMock,
    ) as mock_nonce:
        mock_nonce.return_value = True
        resp = cliente.get("/api/v1/fazendas", headers=headers)
        assert resp.status_code == 401


def test_sec_02_timestamp_fora_da_janela(cliente):
    """SEC-02: Rejeicao 401 quando timestamp estiver fora de +-300s."""
    app.dependency_overrides.pop(exigir_usuario_wordpress, None)
    timestamp_expirado = str(int(time.time()) - 600)

    headers = {
        "X-AgroTracer-Key-Id": "wp-bridge-2026-01",
        "X-AgroTracer-Timestamp": timestamp_expirado,
        "X-AgroTracer-Nonce": "nonce-sec02-expirado",
        "X-AgroTracer-User-Id": "42",
        "X-AgroTracer-Signature": "dummy",
    }
    chave_mock = b"chave_secreta_segura_32_bytes_ok"
    with patch(
        "app.core.bridge_dependency.obter_chave_bridge",
        return_value=chave_mock,
    ):
        resp = cliente.get("/api/v1/fazendas", headers=headers)
        assert resp.status_code == 401


def test_sec_03_anti_replay_nonce_duplicado(cliente):
    """SEC-03: Rejeicao 401 quando nonce ja tiver sido utilizado."""
    app.dependency_overrides.pop(exigir_usuario_wordpress, None)
    timestamp = str(int(time.time()))

    headers = {
        "X-AgroTracer-Key-Id": "wp-bridge-2026-01",
        "X-AgroTracer-Timestamp": timestamp,
        "X-AgroTracer-Nonce": "nonce-sec03-reutilizado",
        "X-AgroTracer-User-Id": "42",
        "X-AgroTracer-Signature": "dummy",
    }
    chave_mock = b"chave_secreta_segura_32_bytes_ok"
    with patch(
        "app.core.bridge_dependency.obter_chave_bridge",
        return_value=chave_mock,
    ), patch(
        "app.core.nonce_store.registrar_nonce",
        new_callable=AsyncMock,
    ) as mock_nonce:
        mock_nonce.return_value = False
        resp = cliente.get("/api/v1/fazendas", headers=headers)
        assert resp.status_code == 401


def test_sec_04_user_id_zero_restricao_sistema(cliente):
    """SEC-04: Rejeicao 403 para wp_user_id zero em rota de usuario."""
    headers = {
        "X-AgroTracer-Key-Id": "wp-bridge-2026-01",
        "X-AgroTracer-Timestamp": str(int(time.time())),
        "X-AgroTracer-Nonce": "nonce-sec04-sistema",
        "X-AgroTracer-User-Id": "0",
        "X-AgroTracer-Signature": "dummy",
    }
    app.dependency_overrides.pop(exigir_usuario_wordpress, None)

    chave_mock = b"chave_secreta_segura_32_bytes_ok"
    with patch(
        "app.core.bridge_dependency.obter_chave_bridge",
        return_value=chave_mock,
    ), patch(
        "app.core.bridge_dependency.verificar_hmac_requisicao",
        new_callable=AsyncMock,
    ) as mock_verificar:
        mock_verificar.return_value = True
        resp = cliente.get("/api/v1/fazendas", headers=headers)
        assert resp.status_code == 403
        dados_erro = resp.json()["error"]
        assert dados_erro["code"] == "AUTH_USER_REQUIRED"
