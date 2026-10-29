import pytest
from sqlalchemy import func, select

from app.models.animal import Animal
from app.models.auditoria_evento import AuditoriaEvento
from app.models.fazenda import Fazenda
from app.models.lote import Lote
from app.models.lote_animal import LoteAnimal
from app.models.produtor import Produtor

# Reutiliza o banco SQLite isolado e a autenticacao de teste
# que ja foram validados na S2-T01.
from test_s2_t01_api import ambiente_api  # noqa: F401


@pytest.fixture
def cenario(request):
    cliente, criar_sessao = request.getfixturevalue("ambiente_api")

    with criar_sessao() as db:
        produtor = Produtor(wordpress_user_id=42)
        outro_produtor = Produtor(wordpress_user_id=84)

        fazenda = Fazenda(
            produtor=produtor,
            nome="Fazenda Principal",
            municipio="Araguari",
            uf="MG",
        )

        fazenda_outra = Fazenda(
            produtor=outro_produtor,
            nome="Fazenda Externa",
            municipio="Uberlandia",
            uf="MG",
        )

        lote_a = Lote(
            fazenda=fazenda,
            codigo_lote="S2T02-LOTE-A",
            status="EM_MANEJO",
        )

        lote_b = Lote(
            fazenda=fazenda,
            codigo_lote="S2T02-LOTE-B",
            status="EM_MANEJO",
        )

        lote_fechado = Lote(
            fazenda=fazenda,
            codigo_lote="S2T02-FECHADO",
            status="FECHADO",
        )

        lote_externo = Lote(
            fazenda=fazenda_outra,
            codigo_lote="S2T02-EXTERNO",
            status="EM_MANEJO",
        )

        animal = Animal(
            produtor=produtor,
            identificador="S2T02-ANIMAL-1",
        )

        animal_externo = Animal(
            produtor=outro_produtor,
            identificador="S2T02-ANIMAL-EXTERNO",
        )

        db.add_all([
            lote_a,
            lote_b,
            lote_fechado,
            lote_externo,
            animal,
            animal_externo,
        ])
        db.flush()

        ids = {
            "lote_a": lote_a.id,
            "lote_b": lote_b.id,
            "lote_fechado": lote_fechado.id,
            "lote_externo": lote_externo.id,
            "animal": animal.id,
            "animal_externo": animal_externo.id,
        }

        db.commit()

    return cliente, criar_sessao, ids


def abrir(cliente, lote_id, animal_id):
    return cliente.post(
        f"/api/v1/lotes/{lote_id}/animais",
        json={"animal_id": animal_id},
    )


def encerrar(cliente, lote_id, animal_id):
    return cliente.delete(
        f"/api/v1/lotes/{lote_id}/animais/{animal_id}"
    )


def test_abrir_associacao_201(cenario):
    cliente, criar_sessao, ids = cenario

    resposta = abrir(
        cliente, ids["lote_a"], ids["animal"]
    )

    assert resposta.status_code == 201

    dados = resposta.json()
    assert dados["animal_id"] == ids["animal"]
    assert dados["lote_id"] == ids["lote_a"]
    assert dados["associado_em"] is not None
    assert dados["desassociado_em"] is None

    with criar_sessao() as db:
        associacao = db.get(LoteAnimal, dados["id"])

        assert associacao is not None
        assert associacao.desassociado_em is None


def test_segunda_associacao_ativa_retorna_409(cenario):
    cliente, criar_sessao, ids = cenario

    primeira = abrir(
        cliente, ids["lote_a"], ids["animal"]
    )
    segunda = abrir(
        cliente, ids["lote_b"], ids["animal"]
    )

    assert primeira.status_code == 201
    assert segunda.status_code == 409

    erro = segunda.json()["error"]
    assert erro["code"] == "ASSOCIACAO_ATIVA_EXISTENTE"
    assert erro["message"]

    with criar_sessao() as db:
        quantidade = db.scalar(
            select(func.count(LoteAnimal.id))
        )
        assert quantidade == 1


def test_encerrar_preserva_linha_historica(cenario):
    cliente, criar_sessao, ids = cenario

    abertura = abrir(
        cliente, ids["lote_a"], ids["animal"]
    )
    assert abertura.status_code == 201

    associacao_id = abertura.json()["id"]

    fechamento = encerrar(
        cliente, ids["lote_a"], ids["animal"]
    )

    assert fechamento.status_code == 200
    assert fechamento.json()["id"] == associacao_id
    assert fechamento.json()["desassociado_em"] is not None

    with criar_sessao() as db:
        associacao = db.get(LoteAnimal, associacao_id)

        assert associacao is not None
        assert associacao.desassociado_em is not None
        assert associacao.desassociado_em >= (
            associacao.associado_em
        )


def test_encerramento_repetido_retorna_409(cenario):
    cliente, criar_sessao, ids = cenario

    assert abrir(
        cliente, ids["lote_a"], ids["animal"]
    ).status_code == 201

    primeira = encerrar(
        cliente, ids["lote_a"], ids["animal"]
    )

    segunda = encerrar(
        cliente, ids["lote_a"], ids["animal"]
    )

    assert primeira.status_code == 200
    assert segunda.status_code == 409

    assert segunda.json()["error"]["code"] == (
        "ASSOCIACAO_NAO_ATIVA"
    )

    with criar_sessao() as db:
        quantidade = db.scalar(
            select(func.count(LoteAnimal.id))
        )
        assert quantidade == 1


def test_reassociar_apos_encerramento(cenario):
    cliente, criar_sessao, ids = cenario

    primeira = abrir(
        cliente, ids["lote_a"], ids["animal"]
    )
    assert primeira.status_code == 201

    fechamento = encerrar(
        cliente, ids["lote_a"], ids["animal"]
    )
    assert fechamento.status_code == 200

    segunda = abrir(
        cliente, ids["lote_b"], ids["animal"]
    )
    assert segunda.status_code == 201

    with criar_sessao() as db:
        associacoes = db.scalars(
            select(LoteAnimal)
            .where(LoteAnimal.animal_id == ids["animal"])
            .order_by(LoteAnimal.id)
        ).all()

        assert len(associacoes) == 2

        assert associacoes[0].lote_id == ids["lote_a"]
        assert associacoes[0].desassociado_em is not None

        assert associacoes[1].lote_id == ids["lote_b"]
        assert associacoes[1].desassociado_em is None


def test_auditoria_abertura_e_encerramento(cenario):
    cliente, criar_sessao, ids = cenario

    abertura = abrir(
        cliente, ids["lote_a"], ids["animal"]
    )
    assert abertura.status_code == 201

    fechamento = encerrar(
        cliente, ids["lote_a"], ids["animal"]
    )
    assert fechamento.status_code == 200

    associacao_id = abertura.json()["id"]

    with criar_sessao() as db:
        eventos = db.scalars(
            select(AuditoriaEvento)
            .where(
                AuditoriaEvento.entidade == "lote_animais",
                AuditoriaEvento.entidade_id == associacao_id,
            )
            .order_by(AuditoriaEvento.id)
        ).all()

        assert len(eventos) == 2

        assert eventos[0].acao == "ABRIR_ASSOCIACAO"
        assert eventos[1].acao == "ENCERRAR_ASSOCIACAO"

        assert all(
            evento.wordpress_user_id == 42
            for evento in eventos
        )


def test_bloqueio_acesso_outro_produtor(cenario):
    cliente, criar_sessao, ids = cenario

    # O usuario 42 nao pode associar animal alheio.
    resposta_animal = abrir(
        cliente,
        ids["lote_a"],
        ids["animal_externo"],
    )
    assert resposta_animal.status_code == 404

    # Tambem nao pode usar lote de outro produtor.
    resposta_lote = abrir(
        cliente,
        ids["lote_externo"],
        ids["animal"],
    )
    assert resposta_lote.status_code == 404

    # Nem encerrar uma associacao em lote alheio.
    resposta_delete = encerrar(
        cliente,
        ids["lote_externo"],
        ids["animal_externo"],
    )
    assert resposta_delete.status_code == 404

    with criar_sessao() as db:
        quantidade = db.scalar(
            select(func.count(LoteAnimal.id))
        )
        assert quantidade == 0


def test_lote_fechado_nao_recebe_animal(cenario):
    cliente, criar_sessao, ids = cenario

    resposta = abrir(
        cliente,
        ids["lote_fechado"],
        ids["animal"],
    )

    assert resposta.status_code == 409
    assert resposta.json()["error"]["code"] == "LOTE_FECHADO"

    with criar_sessao() as db:
        quantidade = db.scalar(
            select(func.count(LoteAnimal.id))
        )
        assert quantidade == 0


def test_payload_invalido_retorna_422(cenario):
    cliente, _, ids = cenario

    negativo = abrir(cliente, ids["lote_a"], -1)
    assert negativo.status_code == 422

    campo_extra = cliente.post(
        f"/api/v1/lotes/{ids['lote_a']}/animais",
        json={
            "animal_id": ids["animal"],
            "produtor_id": 999,
        },
    )

    assert campo_extra.status_code == 422
