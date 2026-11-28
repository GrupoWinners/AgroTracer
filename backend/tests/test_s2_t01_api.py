from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, func, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.bridge_dependency import exigir_usuario_wordpress
from app.db.database import obter_db
from app.main import app
from app.models import Base
from app.models.animal import Animal
from app.models.auditoria_evento import AuditoriaEvento
from app.models.produtor import Produtor
from app.models.fazenda import Fazenda
from app.models.lote import Lote


@compiles(JSONB, "sqlite")
def compilar_jsonb_sqlite(type_, compiler, **kw):
    return "TEXT"


@pytest.fixture
def ambiente_api():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def preparar_sqlite(conexao, registro):
        conexao.create_function(
            "btrim",
            1,
            lambda valor: valor.strip() if valor is not None else "",
        )
        conexao.create_function(
            "char_length",
            1,
            lambda valor: len(valor) if valor is not None else 0,
        )

    SessionTeste = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    def obter_db_teste():
        with SessionTeste() as db:
            yield db

    app.dependency_overrides[obter_db] = obter_db_teste
    app.dependency_overrides[exigir_usuario_wordpress] = lambda: 42
    app.state.redis_cliente = AsyncMock()

    try:
        yield TestClient(app), SessionTeste
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_criar_animal_com_auditoria(ambiente_api):
    cliente, criar_sessao = ambiente_api

    resposta = cliente.post(
        "/api/v1/animais",
        json={
            "identificador": "BR-001",
            "rfid": None,
        },
    )

    assert resposta.status_code == 201

    dados = resposta.json()
    assert dados["identificador"] == "BR-001"
    assert dados["rfid"] is None
    assert dados["id"] > 0
    assert dados["produtor_id"] > 0
    assert "lote_id" not in dados

    with criar_sessao() as db:
        produtor = db.scalar(
            select(Produtor).where(
                Produtor.wordpress_user_id == 42
            )
        )
        assert produtor is not None
        assert dados["produtor_id"] == produtor.id

        animal = db.get(Animal, dados["id"])
        assert animal is not None

        auditoria = db.scalar(
            select(AuditoriaEvento).where(
                AuditoriaEvento.entidade == "animais",
                AuditoriaEvento.entidade_id == animal.id,
                AuditoriaEvento.acao == "CRIAR_ANIMAL",
            )
        )
        assert auditoria is not None
        assert auditoria.wordpress_user_id == 42


def test_identificador_duplicado_retorna_409(ambiente_api):
    cliente, criar_sessao = ambiente_api

    payload = {"identificador": "BR-002"}

    primeira = cliente.post("/api/v1/animais", json=payload)
    segunda = cliente.post("/api/v1/animais", json=payload)

    assert primeira.status_code == 201
    assert segunda.status_code == 409

    erro = segunda.json()["error"]
    assert erro["code"] == "ANIMAL_IDENTIFICADOR_DUPLICADO"

    with criar_sessao() as db:
        quantidade = db.scalar(
            select(func.count(Animal.id))
        )
        assert quantidade == 1

        quantidade_auditoria = db.scalar(
            select(func.count(AuditoriaEvento.id)).where(
                AuditoriaEvento.acao == "CRIAR_ANIMAL"
            )
        )
        assert quantidade_auditoria == 1


def test_bloquear_produtor_informado_pelo_cliente(ambiente_api):
    cliente, _ = ambiente_api

    resposta = cliente.post(
        "/api/v1/animais",
        json={
            "identificador": "BR-003",
            "produtor_id": 999,
        },
    )

    assert resposta.status_code == 422


def test_bloquear_identificador_vazio(ambiente_api):
    cliente, _ = ambiente_api

    resposta = cliente.post(
        "/api/v1/animais",
        json={"identificador": ""},
    )

    assert resposta.status_code == 422


def test_isolamento_lotes_entre_produtores(ambiente_api):
    """RN-19: um produtor nao pode acessar lotes de outro."""
    cliente, criar_sessao = ambiente_api

    with criar_sessao() as db:
        produtor_a = Produtor(wordpress_user_id=42)
        produtor_b = Produtor(wordpress_user_id=84)

        fazenda_a = Fazenda(
            produtor=produtor_a,
            nome="Fazenda A",
            municipio="Araguari",
            uf="MG",
        )

        fazenda_b = Fazenda(
            produtor=produtor_b,
            nome="Fazenda B",
            municipio="Uberlandia",
            uf="MG",
        )

        lote_a = Lote(
            fazenda=fazenda_a,
            codigo_lote="LT-TESTE-A",
            status="EM_MANEJO",
        )

        lote_b = Lote(
            fazenda=fazenda_b,
            codigo_lote="LT-TESTE-B",
            status="EM_MANEJO",
        )

        db.add_all([lote_a, lote_b])
        db.flush()

        id_a = lote_a.id
        id_b = lote_b.id

        db.commit()

    # Usuario WordPress 42 lista somente o proprio lote.
    resposta_lista = cliente.get("/api/v1/lotes")

    assert resposta_lista.status_code == 200

    dados = resposta_lista.json()

    assert len(dados) == 1
    assert dados[0]["id"] == id_a
    assert dados[0]["codigo_lote"] == "LT-TESTE-A"

    # Consultar o proprio lote e permitido.
    resposta_propria = cliente.get(
        f"/api/v1/lotes/{id_a}"
    )

    assert resposta_propria.status_code == 200

    # Consultar lote de outro produtor deve falhar.
    resposta_alheia = cliente.get(
        f"/api/v1/lotes/{id_b}"
    )

    assert resposta_alheia.status_code == 404

    # Um lote inexistente tambem retorna 404.
    resposta_inexistente = cliente.get(
        "/api/v1/lotes/999999"
    )

    assert resposta_inexistente.status_code == 404


def _criar_fazenda_teste(criar_sessao, wp_user_id):
    """Cria uma fazenda ficticia para os testes da API."""
    with criar_sessao() as db:
        produtor = Produtor(wordpress_user_id=wp_user_id)
        fazenda = Fazenda(
            produtor=produtor,
            nome="Fazenda Teste Sprint 2",
            municipio="Araguari",
            uf="MG",
        )
        db.add(fazenda)
        db.commit()
        return fazenda.id


def test_criar_lote_com_auditoria(ambiente_api):
    """Verifica cadastro autorizado e auditoria atomica."""
    cliente, criar_sessao = ambiente_api

    fazenda_id = _criar_fazenda_teste(criar_sessao, 42)

    resposta = cliente.post(
        "/api/v1/lotes",
        json={
            "fazenda_id": fazenda_id,
            "codigo_lote": "LT-S2-001",
        },
    )

    assert resposta.status_code == 201

    dados = resposta.json()
    assert dados["id"] > 0
    assert dados["fazenda_id"] == fazenda_id
    assert dados["codigo_lote"] == "LT-S2-001"

    # Estado inicial provisorio, sujeito a aprovacao da RN-04.
    assert dados["status"] == "RASCUNHO"

    with criar_sessao() as db:
        lote = db.get(Lote, dados["id"])
        assert lote is not None

        auditoria = db.scalar(
            select(AuditoriaEvento).where(
                AuditoriaEvento.entidade == "lotes",
                AuditoriaEvento.entidade_id == lote.id,
                AuditoriaEvento.acao == "CRIAR_LOTE",
            )
        )

        assert auditoria is not None
        assert auditoria.wordpress_user_id == 42


def test_codigo_lote_duplicado_retorna_409(ambiente_api):
    """Garante que dois lotes nao tenham o mesmo codigo."""
    cliente, criar_sessao = ambiente_api

    fazenda_id = _criar_fazenda_teste(criar_sessao, 42)

    payload = {
        "fazenda_id": fazenda_id,
        "codigo_lote": "LT-S2-DUPLICADO",
    }

    primeira = cliente.post("/api/v1/lotes", json=payload)
    segunda = cliente.post("/api/v1/lotes", json=payload)

    assert primeira.status_code == 201
    assert segunda.status_code == 409

    erro = segunda.json()["error"]
    assert erro["code"] == "LOTE_CODIGO_DUPLICADO"

    with criar_sessao() as db:
        total_lotes = db.scalar(select(func.count(Lote.id)))

        total_auditorias = db.scalar(
            select(func.count(AuditoriaEvento.id)).where(
                AuditoriaEvento.acao == "CRIAR_LOTE"
            )
        )

        assert total_lotes == 1
        assert total_auditorias == 1


def test_bloquear_cadastro_em_fazenda_alheia(ambiente_api):
    """RN-19: usuario nao cadastra lote em fazenda alheia."""
    cliente, criar_sessao = ambiente_api

    # Fazenda pertence ao usuario 84.
    # A API esta autenticada como usuario 42.
    fazenda_alheia = _criar_fazenda_teste(
        criar_sessao, 84
    )

    resposta = cliente.post(
        "/api/v1/lotes",
        json={
            "fazenda_id": fazenda_alheia,
            "codigo_lote": "LT-ALHEIO",
        },
    )

    assert resposta.status_code == 404

    with criar_sessao() as db:
        total_lotes = db.scalar(select(func.count(Lote.id)))
        assert total_lotes == 0


def test_status_arbitrario_bloqueado(ambiente_api):
    """Status inicial nao pode ser escolhido pelo cliente."""
    cliente, criar_sessao = ambiente_api

    fazenda_id = _criar_fazenda_teste(criar_sessao, 42)

    resposta = cliente.post(
        "/api/v1/lotes",
        json={
            "fazenda_id": fazenda_id,
            "codigo_lote": "LT-STATUS-INVALIDO",
            "status": "FECHADO",
        },
    )

    assert resposta.status_code == 422

    with criar_sessao() as db:
        total_lotes = db.scalar(select(func.count(Lote.id)))
        assert total_lotes == 0
