import hashlib
from io import BytesIO

import pytest
from pypdf import PdfReader
from sqlalchemy import func, select

from app.models.certificado import Certificado
from app.models.certificado_pdf import CertificadoPDF
from app.models.snapshot_fechamento import SnapshotFechamento
from app.services.certificado_pdf_service import renderizar_pdf
from app.services.certificacao_service import conteudo_snapshot, sha256_json
from test_s2_t01_api import ambiente_api  # noqa: F401
from test_s4_t02_fechamento import fechamento_api  # noqa: F401
from test_s5_t01_certificacao import emitir


def baixar(cenario, ident):
    return cenario[0].get(f"/api/v1/certificados/{ident}/pdf")


def test_pdf_conteudo_hash_e_download_estavel(request, tmp_path):
    cenario = request.getfixturevalue("fechamento_api")
    cert = emitir(cenario).json()
    resposta = baixar(cenario, cert["id"])
    assert resposta.status_code == 200
    assert resposta.headers["content-type"] == "application/pdf"
    assert resposta.headers["cache-control"] == "no-store"
    pdf = resposta.content
    texto = "\n".join(p.extract_text() for p in PdfReader(BytesIO(pdf)).pages)
    for esperado in (
        "CARBONENGINE-MVP-1.0", "S4-DEMO-1", "SYNTHETIC",
        "snapshot_sha256", cert["snapshot_sha256"], "kg CO2e",
    ):
        assert esperado in texto
    for proibido in (cert["token"], "Fazenda Fechamento", "Araguari", "wp:42"):
        assert proibido not in texto
    digest = hashlib.sha256(pdf).hexdigest()
    assert digest not in texto  # sem circularidade
    assert resposta.headers["x-pdf-sha256"] == digest
    with cenario[1]() as db:
        arquivo = db.get(CertificadoPDF, cert["id"])
        assert arquivo.pdf_sha256 == digest
        assert arquivo.conteudo == pdf
    assert baixar(cenario, cert["id"]).content == pdf
    (tmp_path / "certificado-demo.pdf").write_bytes(pdf)


def test_pdf_allowlist_exclui_pii_e_escapa_markup(request):
    cenario = request.getfixturevalue("fechamento_api")
    resposta = emitir(cenario).json()
    with cenario[1]() as db:
        cert = db.get(Certificado, resposta["id"])
        snap = db.get(SnapshotFechamento, cert.snapshot_id)
        snap.entradas["email"] = "privado@example.com"
        snap.entradas["periodos"][0]["proveniencia"][0]["source_uri"] = (
            "https://privado.example/segredo"
        )
        snap.versao_parametros = "<b>versao & teste</b>"
        cert.snapshot_sha256 = sha256_json(conteudo_snapshot(snap))
        pdf = renderizar_pdf(cert, snap)
        texto = "".join(
            p.extract_text() for p in PdfReader(BytesIO(pdf)).pages
        )
        assert "privado" not in texto
        assert "<b>versao & teste</b>" in texto


def test_falha_geracao_nao_persiste_hash_e_permite_retry(request, monkeypatch):
    cenario = request.getfixturevalue("fechamento_api")
    cert = emitir(cenario).json()
    with monkeypatch.context() as contexto:
        contexto.setattr(
            "app.services.certificado_pdf_service.renderizar_pdf",
            lambda *args: (_ for _ in ()).throw(RuntimeError("falha")),
        )
        resposta = baixar(cenario, cert["id"])
        assert resposta.status_code == 503
        assert resposta.json()["error"]["code"] == "PDF_INDISPONIVEL"
    with cenario[1]() as db:
        assert db.scalar(select(func.count(
            CertificadoPDF.certificado_id,
        ))) == 0
        assert db.get(Certificado, cert["id"]).status == "VALIDO"
    assert baixar(cenario, cert["id"]).status_code == 200


def test_snapshot_alterado_nao_gera_pdf(request):
    cenario = request.getfixturevalue("fechamento_api")
    cert = emitir(cenario).json()
    with cenario[1]() as db:
        obj = db.get(Certificado, cert["id"])
        obj.snapshot_sha256 = "0" * 64
        db.commit()
    assert baixar(cenario, cert["id"]).status_code == 409


def test_arquivo_corrompido_nao_e_servido(request):
    cenario = request.getfixturevalue("fechamento_api")
    cert = emitir(cenario).json()
    assert baixar(cenario, cert["id"]).status_code == 200
    with cenario[1]() as db:
        db.get(CertificadoPDF, cert["id"]).conteudo = b"corrompido"
        db.commit()
    assert baixar(cenario, cert["id"]).status_code == 409


def test_download_outro_proprietario_e_ausente(request):
    cenario = request.getfixturevalue("fechamento_api")
    cert = emitir(cenario).json()
    from app.core.bridge_dependency import exigir_usuario_wordpress
    from app.main import app
    app.dependency_overrides[exigir_usuario_wordpress] = lambda: 999
    assert baixar(cenario, cert["id"]).status_code == 404
    assert baixar(cenario, 99999).status_code == 404
    with cenario[1]() as db:
        assert db.scalar(select(func.count(
            CertificadoPDF.certificado_id,
        ))) == 0


@pytest.mark.parametrize("versao", ["A" * 80, "Versão longa " * 6])
def test_pdf_versoes_longas_legiveis(request, versao):
    cenario = request.getfixturevalue("fechamento_api")
    resposta = emitir(cenario).json()
    with cenario[1]() as db:
        cert = db.get(Certificado, resposta["id"])
        snap = db.get(SnapshotFechamento, cert.snapshot_id)
        snap.versao_parametros = versao
        cert.snapshot_sha256 = sha256_json(conteudo_snapshot(snap))
        pdf = renderizar_pdf(cert, snap)
        assert len(PdfReader(BytesIO(pdf)).pages) == 1
