import pytest
from sqlalchemy import func, select

from app.demo_seed import semear, validar_destino
from app.models.certificado import Certificado
from app.models.fazenda import Fazenda
from app.models.fator import Fator
from app.models.produtor import Produtor
from test_s2_t01_api import ambiente_api  # noqa: F401


def test_seed_completo_idempotente_e_sintetico(request):
    _, fabrica = request.getfixturevalue("ambiente_api")
    with fabrica() as db, db.begin():
        criado = semear(db, 42)
        assert criado["criado"] is True
        assert len(criado["token"]) == 43
    with fabrica() as db, db.begin():
        assert semear(db, 42)["criado"] is False
        assert db.scalar(select(func.count(Certificado.id))) == 1
        assert db.scalar(select(func.count(Fazenda.id))) == 1
        assert {f.source_type for f in db.scalars(select(Fator))} == {
            "SYNTHETIC"}
        with pytest.raises(ValueError, match="INCONSISTENTE"):
            semear(db, 99)


def test_seed_recusa_dados_existentes_e_rollback(request, monkeypatch):
    _, fabrica = request.getfixturevalue("ambiente_api")
    with fabrica() as db, db.begin():
        db.add(Produtor(wordpress_user_id=99))
    with fabrica() as db, pytest.raises(ValueError, match="NAO_VAZIO"):
        semear(db, 42)
    with fabrica() as db:
        assert db.scalar(select(func.count(Produtor.id))) == 1
        with pytest.raises(ValueError, match="DESTINO_RECUSADO"):
            validar_destino(db.bind)


def test_seed_rollback_falha_pdf(request, monkeypatch):
    _, fabrica = request.getfixturevalue("ambiente_api")

    def falhar(*args):
        raise RuntimeError("Falha simulada")

    monkeypatch.setattr("app.demo_seed.obter_pdf", falhar)
    with pytest.raises(RuntimeError), fabrica() as db, db.begin():
        semear(db, 42)
    with fabrica() as db:
        assert db.scalar(select(func.count(Produtor.id))) == 0
