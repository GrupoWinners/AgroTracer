from decimal import Decimal
import time
from unittest.mock import AsyncMock, patch
import uuid

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.bridge_dependency import exigir_usuario_wordpress
from app.core.hmac_protocol import build_canonical_string, gerar_assinatura
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


@pytest.fixture
def cliente():
    app.dependency_overrides[obter_db] = override_obter_db
    app.dependency_overrides[exigir_usuario_wordpress] = lambda: 42
    yield TestClient(app)
    app.dependency_overrides.clear()


# ----------------------------------------------------------------------
# 1. MATRIZ DE TESTES CRUD E REGRAS DE NEGOCIO (RF-01 a RF-04)
# ----------------------------------------------------------------------

def test_crud_fazenda_e_talhao_completo(cliente):
    """Fluxo completo de cadastro, listagem, edicao e talhao (RF01-RF04)."""
    # 1. Criar Fazenda
    payload_fazenda = {
        "nome": "Fazenda Bela Vista",
        "municipio": "Aquidauana",
        "uf": "MS",
        "numero_car_informado": (
            "MS-5401209-F38A89BC10D44A6890EF21AA4589CC10"
        ),
    }
    resp = cliente.post("/api/v1/fazendas", json=payload_fazenda)
    assert resp.status_code == 201
    dados_fazenda = resp.json()
    assert dados_fazenda["nome"] == "Fazenda Bela Vista"
    assert dados_fazenda["produtor_id"] > 0
    fazenda_id = dados_fazenda["id"]

    # 2. Listar Fazendas
    resp_lista = cliente.get("/api/v1/fazendas")
    assert resp_lista.status_code == 200
    fazendas = resp_lista.json()
    assert len(fazendas) == 1
    assert fazendas[0]["id"] == fazenda_id

    # 3. Detalhar Fazenda
    resp_detalhe = cliente.get(f"/api/v1/fazendas/{fazenda_id}")
    assert resp_detalhe.status_code == 200
    assert resp_detalhe.json()["municipio"] == "Aquidauana"

    # 4. Editar Fazenda
    resp_edit = cliente.put(
        f"/api/v1/fazendas/{fazenda_id}",
        json={"nome": "Fazenda Bela Vista Atualizada"},
    )
    assert resp_edit.status_code == 200
    assert resp_edit.json()["nome"] == "Fazenda Bela Vista Atualizada"

    # 5. Criar Talhao na Fazenda
    payload_talhao = {
        "identificador": "Piquete 01",
        "area_hectares": "15.5000",
    }
    resp_talhao = cliente.post(
        f"/api/v1/fazendas/{fazenda_id}/talhoes",
        json=payload_talhao,
    )
    assert resp_talhao.status_code == 201
    dados_talhao = resp_talhao.json()
    assert dados_talhao["identificador"] == "Piquete 01"
    assert Decimal(dados_talhao["area_hectares"]) == Decimal("15.5000")
    assert dados_talhao["fazenda_id"] == fazenda_id

    # 6. Listar Talhoes da Fazenda
    resp_talhoes = cliente.get(f"/api/v1/fazendas/{fazenda_id}/talhoes")
    assert resp_talhoes.status_code == 200
    assert len(resp_talhoes.json()) == 1


def test_deduplicacao_car_rn_02(cliente):
    """RN-02: Garantir que o mesmo CAR nao seja cadastrado duas vezes."""
    car = "MS-1234567-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    resp1 = cliente.post("/api/v1/fazendas", json={
        "nome": "Fazenda Alfa",
        "municipio": "Miranda",
        "uf": "MS",
        "numero_car_informado": car,
    })
    assert resp1.status_code == 201

    resp2 = cliente.post("/api/v1/fazendas", json={
        "nome": "Fazenda Beta",
        "municipio": "Miranda",
        "uf": "MS",
        "numero_car_informado": car,
    })
    assert resp2.status_code == 409
    assert "CAR" in resp2.json()["detail"]


def test_validacao_area_positiva_talhao_rn_03(cliente):
    """RN-03: Area do talhao deve ser estritamente maior que zero."""
    resp_f = cliente.post("/api/v1/fazendas", json={
        "nome": "Fazenda Gama",
        "municipio": "Corumba",
        "uf": "MS",
    })
    fazenda_id = resp_f.json()["id"]

    resp_zero = cliente.post(f"/api/v1/fazendas/{fazenda_id}/talhoes", json={
        "identificador": "Piquete Zero",
        "area_hectares": "0",
    })
    assert resp_zero.status_code == 422

    resp_neg = cliente.post(f"/api/v1/fazendas/{fazenda_id}/talhoes", json={
        "identificador": "Piquete Negativo",
        "area_hectares": "-5.5",
    })
    assert resp_neg.status_code == 422


def test_unicidade_identificador_talhao_por_fazenda(cliente):
    """Nao deve permitir dois talhoes com mesmo identificador na fazenda."""
    resp_f = cliente.post("/api/v1/fazendas", json={
        "nome": "Fazenda Delta",
        "municipio": "Coxim",
        "uf": "MS",
    })
    fazenda_id = resp_f.json()["id"]

    resp1 = cliente.post(f"/api/v1/fazendas/{fazenda_id}/talhoes", json={
        "identificador": "Piquete Principal",
        "area_hectares": "20.0",
    })
    assert resp1.status_code == 201

    resp_dup = cliente.post(f"/api/v1/fazendas/{fazenda_id}/talhoes", json={
        "identificador": "Piquete Principal",
        "area_hectares": "10.0",
    })
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

CHAVE_MOCK = b"chave_secreta_segura_32_bytes_ok"


def _montar_headers_hmac(
    method: str = "GET",
    path: str = "/api/v1/fazendas",
    wp_user_id: int = 42,
    timestamp: int | None = None,
    nonce: str | None = None,
    body: bytes = b"",
    chave: bytes = CHAVE_MOCK,
    correlation_id: str | None = None,
) -> tuple[dict[str, str], str]:
    if timestamp is None:
        timestamp = int(time.time())
    if nonce is None:
        nonce = uuid.uuid4().hex
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())

    canonical = build_canonical_string(
        method=method,
        path_with_query=path,
        timestamp=timestamp,
        nonce=nonce,
        wp_user_id=wp_user_id,
        body=body,
    )
    sig = gerar_assinatura(canonical, chave)

    headers = {
        "X-AgroTracer-Key-Id": "wp-bridge-2026-01",
        "X-AgroTracer-Timestamp": str(timestamp),
        "X-AgroTracer-Nonce": nonce,
        "X-AgroTracer-User-Id": str(wp_user_id),
        "X-AgroTracer-Signature": sig,
        "X-Correlation-ID": correlation_id,
    }
    return headers, sig


def test_sec_01_hmac_tampering(cliente):
    """SEC-01: Rejeicao 401 quando assinatura HMAC for adulterada."""
    app.dependency_overrides.pop(exigir_usuario_wordpress, None)

    headers, _ = _montar_headers_hmac(method="GET", path="/api/v1/fazendas")
    # Adultera a assinatura (mantendo hex 64 chars para testar o HMAC)
    headers["X-AgroTracer-Signature"] = "0" * 64

    with patch(
        "app.core.bridge_dependency.obter_chave_bridge",
        return_value=CHAVE_MOCK,
    ), patch(
        "app.core.bridge_auth.registrar_nonce",
        new_callable=AsyncMock,
    ) as mock_nonce:
        mock_nonce.return_value = True
        resp = cliente.get("/api/v1/fazendas", headers=headers)
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "AUTH_INVALID_REQUEST"


def test_sec_02_timestamp_fora_da_janela(cliente):
    """SEC-02: Rejeicao 401 quando timestamp estiver fora de +-300s."""
    app.dependency_overrides.pop(exigir_usuario_wordpress, None)
    timestamp_expirado = int(time.time()) - 600

    headers, _ = _montar_headers_hmac(
        method="GET",
        path="/api/v1/fazendas",
        timestamp=timestamp_expirado,
    )

    with patch(
        "app.core.bridge_dependency.obter_chave_bridge",
        return_value=CHAVE_MOCK,
    ):
        resp = cliente.get("/api/v1/fazendas", headers=headers)
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "AUTH_INVALID_REQUEST"


def test_sec_03_anti_replay_nonce_duplicado(cliente):
    """SEC-03: Rejeicao 401 quando nonce ja tiver sido utilizado."""
    app.dependency_overrides.pop(exigir_usuario_wordpress, None)

    headers, _ = _montar_headers_hmac(method="GET", path="/api/v1/fazendas")

    with patch(
        "app.core.bridge_dependency.obter_chave_bridge",
        return_value=CHAVE_MOCK,
    ), patch(
        "app.core.bridge_auth.registrar_nonce",
        new_callable=AsyncMock,
    ) as mock_nonce:
        mock_nonce.return_value = False
        resp = cliente.get("/api/v1/fazendas", headers=headers)
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "AUTH_INVALID_REQUEST"
        mock_nonce.assert_awaited_once()


def test_sec_04_user_id_zero_restricao_sistema(cliente):
    """SEC-04: Rejeicao 403 para wp_user_id zero em rota de usuario."""
    app.dependency_overrides.pop(exigir_usuario_wordpress, None)

    headers, _ = _montar_headers_hmac(
        method="GET",
        path="/api/v1/fazendas",
        wp_user_id=0,
    )

    with patch(
        "app.core.bridge_dependency.obter_chave_bridge",
        return_value=CHAVE_MOCK,
    ), patch(
        "app.core.bridge_auth.registrar_nonce",
        new_callable=AsyncMock,
    ) as mock_nonce:
        mock_nonce.return_value = True
        resp = cliente.get("/api/v1/fazendas", headers=headers)
        assert resp.status_code == 403
        dados_erro = resp.json()["error"]
        assert dados_erro["code"] == "AUTH_USER_REQUIRED"
