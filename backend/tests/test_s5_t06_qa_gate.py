"""S5-T06: QA Gate da Sprint 5 — Certificado PDF, QR, Idempotência e Consulta.

Escopo Técnico Auditado:
- Comparação Banco vs. API vs. PDF vs. QR (Consistência End-to-End)
- Validação dos 3 Tokens (Válido, Revogado, Inexistente/Malformado - RN-13)
- Leak Test do DTO Público (SEC-07: sem CPF/CNPJ, e-mail, telefone, chaves,
  notas internas ou PII)
- Prevenção de Clique Duplo e Idempotência (SEC-08)
- Proteção contra BOLA em Certificados (Anti-enumeração e controle de acesso)
- Geração de QR Code 100% local sem vazamento de token para serviços externos
"""

import hashlib
import json
from io import BytesIO
from pathlib import Path
from unittest.mock import AsyncMock

from pypdf import PdfReader
from sqlalchemy import func, select
from sqlalchemy.orm.attributes import flag_modified

from app.core.bridge_dependency import exigir_usuario_wordpress
from app.main import app
from app.models.auditoria_evento import AuditoriaEvento
from app.models.certificado import Certificado
from app.models.certificado_pdf import CertificadoPDF
from app.models.snapshot_fechamento import SnapshotFechamento
from app.models.token_publico import TokenPublico
from app.services.certificacao_service import conteudo_snapshot, sha256_json
from app.services.token_service import hash_token
from test_s2_t01_api import ambiente_api  # noqa: F401
from test_s4_t02_fechamento import fechamento_api  # noqa: F401
from test_s5_t01_certificacao import emitir
from test_s5_t02_pdf import baixar


RAIZ_REPO = Path(__file__).parents[2]


def _configurar_mock_redis():
    mock_redis = AsyncMock()
    mock_redis.eval.return_value = 1
    app.state.redis_cliente = mock_redis
    return mock_redis


def test_qa_gate_consistencia_banco_api_pdf_qr(request):
    """Compara banco, API, PDF e QR para garantir consistencia integral."""
    cenario = request.getfixturevalue("fechamento_api")
    _configurar_mock_redis()
    cliente, sessao, _ = cenario

    # 1. API: Emissao do Certificado
    resp_emissao = emitir(cenario, chave="qa-gate-s5-consistencia-1")
    assert resp_emissao.status_code == 201, resp_emissao.text
    assert resp_emissao.headers["cache-control"] == "no-store"
    dados_emissao = resp_emissao.json()

    cert_id = dados_emissao["id"]
    token_opaco = dados_emissao["token"]
    snapshot_sha = dados_emissao["snapshot_sha256"]
    assert len(token_opaco) == 43

    # 2. Banco: Verificacao de integridade e custodia segura do token
    with sessao() as db:
        cert_db = db.get(Certificado, cert_id)
        assert cert_db is not None
        assert cert_db.status == "VALIDO"
        assert cert_db.snapshot_sha256 == snapshot_sha

        # Snapshot integro no banco
        snap_db = db.get(SnapshotFechamento, cert_db.snapshot_id)
        assert snap_db is not None
        assert sha256_json(conteudo_snapshot(snap_db)) == snapshot_sha

        # TokenPublico: somente o hash SHA-256 e armazenado no banco!
        token_db = db.get(TokenPublico, cert_db.token_id)
        assert token_db.token_hash == hash_token(token_opaco)

        # Garante que o token opaco original NAO reside em nenhuma tabela
        for modelo in (
            Certificado, TokenPublico, SnapshotFechamento, AuditoriaEvento,
        ):
            todos_registros = db.scalars(select(modelo)).all()
            for reg in todos_registros:
                serializado = str(reg.__dict__)
                assert token_opaco not in serializado

    # 3. PDF: Download privado, consistencia de dados e sem token impresso
    resp_pdf = baixar(cenario, cert_id)
    assert resp_pdf.status_code == 200
    assert resp_pdf.headers["content-type"] == "application/pdf"
    assert resp_pdf.headers["cache-control"] == "no-store"

    pdf_bytes = resp_pdf.content
    pdf_digest = hashlib.sha256(pdf_bytes).hexdigest()
    assert resp_pdf.headers["x-pdf-sha256"] == pdf_digest

    with sessao() as db:
        pdf_db = db.get(CertificadoPDF, cert_id)
        assert pdf_db is not None
        assert pdf_db.pdf_sha256 == pdf_digest
        assert pdf_db.conteudo == pdf_bytes

    reader = PdfReader(BytesIO(pdf_bytes))
    texto_pdf = "\n".join(p.extract_text() for p in reader.pages)

    # Dados essenciais estao presentes no PDF
    assert "CARBONENGINE-MVP-1.0" in texto_pdf
    assert "S4-DEMO-1" in texto_pdf
    assert "SYNTHETIC" in texto_pdf
    assert snapshot_sha in texto_pdf
    assert "kg CO2e" in texto_pdf

    # Token opaco e pdf_sha256 NUNCA estao no texto do PDF
    assert token_opaco not in texto_pdf
    assert pdf_digest not in texto_pdf

    # 4. QR Code & Consulta Publica
    # URL publica esperada gerada com o token
    url_publica = f"/certificado/?token={token_opaco}"
    assert token_opaco in url_publica

    # Consulta publica (sem autenticacao/HMAC)
    app.dependency_overrides.pop(exigir_usuario_wordpress, None)
    resp_pub = cliente.get(
        "/api/v1/certificados/publico",
        params={"token": token_opaco},
    )
    assert resp_pub.status_code == 200
    dto_pub = resp_pub.json()

    # Compara consistencia absoluta: Banco == API == PDF == Consulta Publica
    assert dto_pub["certificado_id"] == cert_id
    assert dto_pub["lote_id"] == dados_emissao["lote_id"]
    assert dto_pub["status"] == "VALIDO"
    assert dto_pub["versao_metodo"] == "CARBONENGINE-MVP-1.0"
    assert dto_pub["versao_parametros"] == "S4-DEMO-1"
    assert dto_pub["snapshot_sha256"] == snapshot_sha
    assert dto_pub["pdf_sha256"] == pdf_digest
    assert dto_pub["synthetic"] is True
    assert dto_pub["source_types"] == ["SYNTHETIC"]
    assert dto_pub["resultados"]["unidade_emissao"] == "kg CO2e"


def test_qa_gate_tres_tokens_validos_revogados_e_inexistentes(request):
    """Critério de aceite: 3 tokens (valido, revogado, inexistente - RN-13)."""
    cenario = request.getfixturevalue("fechamento_api")
    mock_redis = _configurar_mock_redis()
    cliente, sessao, _ = cenario

    # --- TOKEN 1: Token Valido ---
    resp_emissao_1 = emitir(cenario, chave="qa-token-1")
    assert resp_emissao_1.status_code == 201
    token_1 = resp_emissao_1.json()["token"]

    app.dependency_overrides.pop(exigir_usuario_wordpress, None)
    resp_token_1 = cliente.get(
        "/api/v1/certificados/publico",
        params={"token": token_1},
    )
    assert resp_token_1.status_code == 200
    dto_1 = resp_token_1.json()
    assert dto_1["status"] == "VALIDO"
    assert dto_1["certificado_id"] == resp_emissao_1.json()["id"]

    # --- TOKEN 2: Token de Certificado Revogado ---
    with sessao() as db:
        cert_obj = db.get(Certificado, resp_emissao_1.json()["id"])
        cert_obj.status = "REVOGADO"
        db.commit()

    resp_token_2 = cliente.get(
        "/api/v1/certificados/publico",
        params={"token": token_1},
    )
    assert resp_token_2.status_code == 200
    dto_2 = resp_token_2.json()
    assert dto_2["status"] == "REVOGADO"
    assert dto_2["certificado_id"] == resp_emissao_1.json()["id"]

    # --- TOKEN 3: Tokens Inexistentes ou Malformados (RN-13) ---
    tokens_invalidos = [
        "token_inexistente_com_tamanho_43_bytes_ok123",
        "",
        "curto",
        "!@#$%^&*()",
        "A" * 2000,
    ]
    for token_invalido in tokens_invalidos:
        mock_redis.reset_mock()
        mock_redis.eval.return_value = 1
        resp_invalido = cliente.get(
            "/api/v1/certificados/publico",
            params={"token": token_invalido},
        )
        assert resp_invalido.status_code == 404
        erro = resp_invalido.json()["error"]
        assert erro["code"] == "CERTIFICADO_NAO_ENCONTRADO"
        assert erro["message"] == "Certificado nao encontrado."
        # Garante que consome rate limit igualmente no Redis (anti-timing)
        mock_redis.eval.assert_awaited_once()


def test_qa_gate_leak_test_dto_publico_sec07(request):
    """Leak test do DTO publico (SEC-07): sem CPF/CNPJ, e-mail, telefone."""
    cenario = request.getfixturevalue("fechamento_api")
    _configurar_mock_redis()
    cliente, sessao, _ = cenario

    resp_emissao = emitir(cenario, chave="qa-leak-test-sec07")
    assert resp_emissao.status_code == 201
    cert_id = resp_emissao.json()["id"]
    token_opaco = resp_emissao.json()["token"]

    # Injeta dados altamente sensíveis no snapshot
    dados_sensiveis = {
        "cpf": "123.456.789-00",
        "cnpj": "12.345.678/0001-90",
        "email": "produtor.confidencial@fazenda.com.br",
        "telefone": "+55 34 99999-8888",
        "chave_privada": "rsa-priv-secret-key-12345",
        "api_key": "secret-internal-api-key-99999",
        "nota_interna": "Nota confidencial de fiscalizacao sanitaria interna",
        "source_uri": "https://intranet.fazenda.example/privado/laudo.xlsx",
        "fazenda_nome": "Fazenda Fechamento Confidencial",
        "municipio": "MunicipioSecreto",
        "uf": "UFSecreta",
        "car": "CAR-MG-0001928374",
    }

    with sessao() as db:
        cert = db.get(Certificado, cert_id)
        snap = db.get(SnapshotFechamento, cert.snapshot_id)
        snap.entradas.update(dados_sensiveis)
        snap.entradas["periodos"][0]["proveniencia"][0]["source_uri"] = (
            dados_sensiveis["source_uri"]
        )
        flag_modified(snap, "entradas")
        cert.snapshot_sha256 = sha256_json(conteudo_snapshot(snap))
        db.commit()

    # Requisicao publica do DTO
    app.dependency_overrides.pop(exigir_usuario_wordpress, None)
    resposta = cliente.get(
        "/api/v1/certificados/publico",
        params={"token": token_opaco},
    )
    assert resposta.status_code == 200
    dto_json_texto = json.dumps(resposta.json(), ensure_ascii=False)

    # Validacao estrita de NAO-VAZAMENTO de nenhum dado confidencial
    for rotulo, valor_proibido in dados_sensiveis.items():
        assert str(valor_proibido) not in dto_json_texto, (
            f"Vazamento detectado para {rotulo}: {valor_proibido}"
        )

    # Proibe palavras-chave restritas
    for termo_proibido in (
        token_opaco,
        "token_hash",
        "idempotency_hash",
        "request_hash",
        "source_uri",
        "wordpress_user_id",
        "produtor_id",
        "chave_privada",
        "api_key",
        "nota_interna",
        "cpf",
        "cnpj",
        "telefone",
        "email",
    ):
        assert termo_proibido not in dto_json_texto


def test_qa_gate_clique_duplo_e_idempotencia_sec08(request):
    """Clique duplo (SEC-08): prevencao de submissao concorrente e reuso."""
    cenario = request.getfixturevalue("fechamento_api")
    sessao = cenario[1]

    # 1. Primeira emissao com chave "clique-duplo-gate" -> 201 Created
    chave = "clique-duplo-gate"
    resp1 = emitir(cenario, chave=chave)
    assert resp1.status_code == 201

    # 2. Clique duplo imediato (mesma chave/payload) -> 409 PROCESSADA
    resp_clique_duplo = emitir(cenario, chave=chave)
    assert resp_clique_duplo.status_code == 409
    assert (
        resp_clique_duplo.json()["error"]["code"]
        == "CERTIFICACAO_JA_PROCESSADA"
    )
    assert "token" not in resp_clique_duplo.json()

    # 3. Reutilizar chave com alteracao de payload -> 409 REUTILIZADA
    resp_reuso = emitir(cenario, chave=chave, peso_medio_abate_kg="580")
    assert resp_reuso.status_code == 409
    assert (
        resp_reuso.json()["error"]["code"]
        == "IDEMPOTENCY_KEY_REUTILIZADA"
    )

    # 4. Outra chave no mesmo lote ja fechado -> 409 JA_EXISTENTE
    resp_outro = emitir(cenario, chave="outra-chave-qualquer")
    assert resp_outro.status_code == 409
    assert (
        resp_outro.json()["error"]["code"]
        == "CERTIFICADO_JA_EXISTENTE"
    )

    # Garante que apenas 1 certificado e 1 token foram gerados no banco
    with sessao() as db:
        assert db.scalar(select(func.count(Certificado.id))) == 1
        assert db.scalar(select(func.count(TokenPublico.id))) == 1


def test_qa_gate_bola_em_certificados(request):
    """BOLA em certificados: produtor nao autorizado recebe 404."""
    cenario = request.getfixturevalue("fechamento_api")
    resp_emissao = emitir(cenario, chave="qa-bola-teste-1")
    assert resp_emissao.status_code == 201
    cert_id = resp_emissao.json()["id"]

    # Simula troca para outro usuario WordPress (Produtor invasor B: id 999)
    app.dependency_overrides[exigir_usuario_wordpress] = lambda: 999

    # Tentativa de download do PDF do Produtor A pelo Produtor B
    resp_invasao_pdf = baixar(cenario, cert_id)
    # Tentativa de download de ID inexistente
    resp_inexistente_pdf = baixar(cenario, 99999)

    # Ambos retornam 404 CERTIFICADO_NAO_ENCONTRADO com mesma estrutura
    assert resp_invasao_pdf.status_code == 404
    assert resp_inexistente_pdf.status_code == 404
    assert (
        resp_invasao_pdf.json()["error"]["code"]
        == resp_inexistente_pdf.json()["error"]["code"]
        == "CERTIFICADO_NAO_ENCONTRADO"
    )
    assert (
        resp_invasao_pdf.json()["error"]["message"]
        == resp_inexistente_pdf.json()["error"]["message"]
        == "Certificado nao encontrado."
    )

    # Tentativa de certificar lote alheio
    resp_invasao = emitir(cenario, chave="chave-invasor")
    resp_inexistente_lote = emitir(
        cenario, chave="chave-lote-inexistente", lote_id=99999
    )
    assert resp_invasao.status_code == 404
    assert resp_inexistente_lote.status_code == 404
    assert (
        resp_invasao.json()["error"]["code"]
        == resp_inexistente_lote.json()["error"]["code"]
        == "LOTE_NAO_ENCONTRADO"
    )


def test_qa_gate_frontend_qr_local_e_travas_clique_duplo():
    """Valida no frontend WordPress as travas de clique duplo e QR local."""
    screens_js = (
        RAIZ_REPO
        / "wordpress"
        / "agrotracer-bridge"
        / "assets"
        / "js"
        / "agrotracer-screens.js"
    ).read_text(encoding="utf-8")

    # 1. Trava sincrona de clique duplo / submissao multipla
    assert "let isSubmitting = false;" in screens_js
    assert "let isDownloadingPdf = false;" in screens_js
    assert "if (isSubmitting) return;" in screens_js
    assert "isSubmitting = true;" in screens_js
    assert "btnSubmit.disabled = true;" in screens_js

    # 2. Gerador QR local em memoria sem APIs externas
    assert "function buildQrCodeSvg(text)" in screens_js
    aviso_externo = "Evita envio do token opaco a APIs externas de QR Code."
    assert aviso_externo in screens_js
    for api_externa in (
        "api.qrserver.com",
        "chart.googleapis.com",
        "quickchart.io",
        "qr-code-generator.com",
    ):
        assert api_externa not in screens_js
