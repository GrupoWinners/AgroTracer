"""S5-T02: PDF minimizado, derivado exclusivamente do snapshot certificado."""

import hashlib
from functools import partial
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    HRFlowable, Paragraph, SimpleDocTemplate, Spacer,
)

from app.models.certificado_pdf import CertificadoPDF
from app.services.certificacao_service import conteudo_snapshot, sha256_json
from app.services.fechamento_service import ErroFechamento


def renderizar_pdf(certificado, snapshot):
    if sha256_json(conteudo_snapshot(snapshot)) != certificado.snapshot_sha256:
        raise ErroFechamento(
            409, "SNAPSHOT_INTEGRO_OBRIGATORIO",
            "Snapshot nao corresponde ao certificado.",
        )
    estilos = getSampleStyleSheet()
    estilos.add(ParagraphStyle(
        "Marca", fontName="Helvetica-Bold", fontSize=12,
        textColor=colors.HexColor("#246B50"), spaceAfter=16,
    ))
    estilos.add(ParagraphStyle(
        "Digest", fontName="Courier", fontSize=8, leading=12,
        spaceAfter=14,
    ))
    saida = BytesIO()
    documento = SimpleDocTemplate(
        saida, pagesize=A4, rightMargin=48, leftMargin=48,
        topMargin=44, bottomMargin=44, title="Certificado AgroTracer",
        author="AgroTracer",
    )
    itens = [
        Paragraph("AGROTRACER", estilos["Marca"]),
        Paragraph("Certificado de emissões", estilos["Title"]),
        Paragraph(
            f"Registro {certificado.id} | Lote {certificado.lote_id}",
            estilos["Normal"],
        ),
        Spacer(1, 16),
        HRFlowable(width="100%", color=colors.HexColor("#246B50")),
    ]

    def campo(rotulo, valor):
        itens.append(Paragraph(
            f"<b>{escape(rotulo)}:</b> {escape(str(valor))}",
            estilos["BodyText"],
        ))

    tipos = sorted({
        origem["source_type"]
        for periodo in snapshot.entradas["periodos"]
        for origem in periodo["proveniencia"]
    })
    itens.append(Paragraph("Método e proveniência", estilos["Heading2"]))
    campo("Versão do método", snapshot.versao_metodo)
    campo("Versão dos parâmetros", snapshot.versao_parametros)
    campo("source_type", ", ".join(tipos))
    if "SYNTHETIC" in tipos:
        itens.append(Paragraph(
            "<b>SYNTHETIC - DEMONSTRAÇÃO DIDÁTICA.</b> "
            "Contém fatores sintéticos. Não representa validação científica "
            "ou certificação ambiental independente.", estilos["BodyText"],
        ))
    itens.append(Paragraph("Resultados do snapshot", estilos["Heading2"]))
    campo("Emissão total (kg CO2e)",
          snapshot.resultados["emissao_total_kg_co2e"])
    campo("Intensidade (kg CO2e/kg de carcaça)",
          snapshot.resultados["intensidade_kg_co2e_kg"])
    campo("Data de abate", snapshot.entradas["data_abate"])
    campo("Animais no abate", snapshot.entradas["numero_animais_abate"])
    itens.append(Paragraph("Integridade", estilos["Heading2"]))
    campo("snapshot_sha256", "SHA-256 do snapshot canônico (schema 1)")
    itens.append(Paragraph(certificado.snapshot_sha256, estilos["Digest"]))
    itens.append(Paragraph(
        "Documento gerado a partir do registro imutável. O hash do arquivo "
        "PDF é armazenado separadamente após a geração.",
        estilos["BodyText"],
    ))
    documento.build(itens, canvasmaker=partial(Canvas, invariant=1))
    return saida.getvalue()


def obter_pdf(db, certificado, snapshot):
    """Chamador bloqueia certificado. Nao faz commit nem grava filesystem."""
    arquivo = db.get(CertificadoPDF, certificado.id)
    if arquivo is None:
        conteudo = renderizar_pdf(certificado, snapshot)
        arquivo = CertificadoPDF(
            certificado_id=certificado.id, conteudo=conteudo,
            pdf_sha256=hashlib.sha256(conteudo).hexdigest(),
        )
        db.add(arquivo)
        db.flush()
    elif hashlib.sha256(arquivo.conteudo).hexdigest() != arquivo.pdf_sha256:
        raise ErroFechamento(
            409, "PDF_INTEGRIDADE_INVALIDA",
            "Arquivo nao corresponde ao hash registrado.",
        )
    return arquivo
