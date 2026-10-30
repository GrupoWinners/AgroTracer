import pytest
from sqlalchemy import func, select

from app.models.animal import Animal
from app.models.auditoria_evento import AuditoriaEvento
from app.models.fazenda import Fazenda
from app.models.lote import Lote
from app.models.movimentacao import Movimentacao
from app.models.produtor import Produtor

from test_s2_t01_api import ambiente_api  # noqa: F401


@pytest.fixture
def cenario(request):
    cliente, criar_sessao = request.getfixturevalue("ambiente_api")

    with criar_sessao() as db:
        dono = Produtor(wordpress_user_id=42)
        outro = Produtor(wordpress_user_id=84)

        fazenda = Fazenda(
            produtor=dono,
            nome="Fazenda S2T03",
            municipio="Araguari",
            uf="MG",
        )
        fazenda_outra = Fazenda(
            produtor=outro,
            nome="Fazenda Externa S2T03",
            municipio="Uberlandia",
            uf="MG",
        )

        lote = Lote(
            fazenda=fazenda,
            codigo_lote="S2T03-LOTE-01",
            status="EM_MANEJO",
        )
        lote_outro = Lote(
            fazenda=fazenda_outra,
            codigo_lote="S2T03-LOTE-02",
            status="EM_MANEJO",
        )

        animal = Animal(
            produtor=dono,
            identificador="S2T03-ANIMAL-01",
        )
        animal_outro = Animal(
            produtor=outro,
            identificador="S2T03-ANIMAL-02",
        )

        db.add_all([
            lote,
            lote_outro,
            animal,
            animal_outro,
        ])
        db.flush()

        ids = {
            "animal": animal.id,
            "animal_outro": animal_outro.id,
            "lote": lote.id,
            "lote_outro": lote_outro.id,
        }
        db.commit()

    return cliente, criar_sessao, ids


def enviar(cliente, **campos):
    payload = {
        "tipo": "TRANSFERENCIA",
        "data_hora": "2027-01-10T12:00:00Z",
        **campos,
    }
    return cliente.post(
        "/api/v1/movimentacoes",
        json=payload,
    )


def test_movimentacao_animal_e_auditoria(cenario):
    cliente, sessao, ids = cenario

    resposta = enviar(cliente, animal_id=ids["animal"])

    assert resposta.status_code == 201, resposta.text
    dados = resposta.json()

    assert dados["animal_id"] == ids["animal"]
    assert dados["lote_id"] is None
    assert dados["id"] > 0

    with sessao() as db:
        movimento = db.get(Movimentacao, dados["id"])
        assert movimento is not None

        auditoria = db.scalar(
            select(AuditoriaEvento).where(
                AuditoriaEvento.entidade == "movimentacoes",
                AuditoriaEvento.entidade_id == movimento.id,
                AuditoriaEvento.acao == "CRIAR_MOVIMENTACAO",
            )
        )

        assert auditoria is not None
        assert auditoria.wordpress_user_id == 42


def test_movimentacao_lote(cenario):
    cliente, sessao, ids = cenario

    resposta = enviar(cliente, lote_id=ids["lote"])

    assert resposta.status_code == 201, resposta.text
    assert resposta.json()["lote_id"] == ids["lote"]
    assert resposta.json()["animal_id"] is None

    with sessao() as db:
        assert db.scalar(
            select(func.count(Movimentacao.id))
        ) == 1


@pytest.mark.parametrize(
    "alvos",
    [
        {},
        {"animal_id": 1, "lote_id": 1},
    ],
)
def test_rejeitar_zero_ou_dois_alvos(cenario, alvos):
    cliente, sessao, _ = cenario

    resposta = enviar(cliente, **alvos)

    assert resposta.status_code == 422

    with sessao() as db:
        assert db.scalar(
            select(func.count(Movimentacao.id))
        ) == 0


def test_rejeitar_origem_igual_destino(cenario):
    cliente, sessao, ids = cenario

    resposta = enviar(
        cliente,
        animal_id=ids["animal"],
        origem_talhao_id=123,
        destino_talhao_id=123,
    )

    assert resposta.status_code == 422

    with sessao() as db:
        assert db.scalar(
            select(func.count(Movimentacao.id))
        ) == 0


def test_cronologia_e_rollback(cenario):
    cliente, sessao, ids = cenario

    primeira = enviar(
        cliente,
        animal_id=ids["animal"],
        data_hora="2027-01-10T12:00:00Z",
    )
    assert primeira.status_code == 201

    anterior = enviar(
        cliente,
        animal_id=ids["animal"],
        data_hora="2027-01-09T12:00:00Z",
    )
    assert anterior.status_code == 409
    assert anterior.json()["error"]["code"] == (
        "MOVIMENTACAO_FORA_DE_ORDEM"
    )

    repetida = enviar(
        cliente,
        animal_id=ids["animal"],
        data_hora="2027-01-10T12:00:00Z",
    )
    assert repetida.status_code == 409

    posterior = enviar(
        cliente,
        animal_id=ids["animal"],
        data_hora="2027-01-11T12:00:00Z",
    )
    assert posterior.status_code == 201

    with sessao() as db:
        assert db.scalar(
            select(func.count(Movimentacao.id))
        ) == 2

        assert db.scalar(
            select(func.count(AuditoriaEvento.id)).where(
                AuditoriaEvento.acao == "CRIAR_MOVIMENTACAO"
            )
        ) == 2


def test_bloquear_animal_e_lote_de_terceiro(cenario):
    cliente, sessao, ids = cenario

    animal = enviar(
        cliente,
        animal_id=ids["animal_outro"],
    )
    lote = enviar(
        cliente,
        lote_id=ids["lote_outro"],
    )

    assert animal.status_code == 404
    assert lote.status_code == 404

    with sessao() as db:
        assert db.scalar(
            select(func.count(Movimentacao.id))
        ) == 0


def test_bloquear_talhao_inexistente(cenario):
    cliente, sessao, ids = cenario

    resposta = enviar(
        cliente,
        animal_id=ids["animal"],
        origem_talhao_id=999999999,
    )

    assert resposta.status_code == 404
    assert resposta.json()["error"]["code"] == (
        "TALHAO_NAO_ENCONTRADO"
    )

    with sessao() as db:
        assert db.scalar(
            select(func.count(Movimentacao.id))
        ) == 0


def test_data_sem_timezone_e_campo_extra(cenario):
    cliente, _, ids = cenario

    sem_timezone = enviar(
        cliente,
        animal_id=ids["animal"],
        data_hora="2027-01-10T12:00:00",
    )

    campo_extra = enviar(
        cliente,
        animal_id=ids["animal"],
        produtor_id=999,
    )

    assert sem_timezone.status_code == 422
    assert campo_extra.status_code == 422
