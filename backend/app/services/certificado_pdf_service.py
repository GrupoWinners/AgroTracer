"""S5-T02: PDF timbrado A4, derivado exclusivamente do snapshot certificado."""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from functools import lru_cache, partial
import hashlib
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

from app.models.certificado_pdf import CertificadoPDF
from app.services.certificacao_service import conteudo_snapshot, sha256_json
from app.services.fechamento_service import ErroFechamento

COR_PRIMARIA = colors.HexColor("#163A28")
COR_SECUNDARIA = colors.HexColor("#2F6F4E")
COR_ACENTO = colors.HexColor("#7BB661")
COR_GRAFITE = colors.HexColor("#2B3033")
COR_LABEL = colors.HexColor("#5A6266")
COR_CARD = colors.HexColor("#F4F7F5")
COR_BORDA = colors.HexColor("#E1E8E4")
COR_ALERTA_BG = colors.HexColor("#FFF8E6")
COR_ALERTA_BORDA = colors.HexColor("#E6B84C")
COR_ALERTA_TXT = colors.HexColor("#7A5600")
ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"


@lru_cache(maxsize=2)
def _carregar_imagem(nome: str) -> ImageReader | None:
    caminho = ASSETS_DIR / nome
    if not caminho.is_file():
        return None
    return ImageReader(BytesIO(caminho.read_bytes()))


def _formatar_decimal_br(valor, casas_min=2, casas_max=4) -> str:
    bruto = str(valor or "0").strip()
    try:
        dec = Decimal(bruto)
    except InvalidOperation:
        return bruto
    quant = Decimal("10") ** (-casas_max)
    arred = dec.quantize(quant, rounding=ROUND_HALF_UP)
    sinal = "-" if arred < 0 else ""
    texto = f"{abs(arred):.{casas_max}f}"
    inteiro, frac = texto.split(".")
    frac_limpa = frac.rstrip("0")
    if len(frac_limpa) < casas_min:
        frac_limpa = frac_limpa.ljust(casas_min, "0")
    int_fmt = f"{int(inteiro):,}".replace(",", ".")
    return f"{sinal}{int_fmt},{frac_limpa}"


def _formatar_data_br(data_iso) -> str:
    texto = str(data_iso or "").strip()
    partes = texto.split("-")
    if len(partes) == 3 and all(p.isdigit() for p in partes):
        return f"{partes[2]}/{partes[1]}/{partes[0]}"
    return texto or "—"


def _desenhar_papel_timbrado(certificado, data_ref, canvas: Canvas, doc):
    canvas.saveState()
    largura, altura = A4

    # 1. Marca d'agua centralizada (emblema ~5.5% opacidade em fundo branco)
    marca_dagua = _carregar_imagem("logo-agrotracer-watermark.png")
    if marca_dagua is not None:
        tam_wm = 250
        canvas.drawImage(
            marca_dagua,
            (largura - tam_wm) / 2.0,
            (altura - tam_wm) / 2.0 - 14,
            width=tam_wm,
            height=tam_wm,
            mask="auto",
        )

    # 2. Moldura interna minimalista do papel timbrado
    margem_m = 22
    canvas.setStrokeColor(COR_BORDA)
    canvas.setLineWidth(0.75)
    canvas.roundRect(
        margem_m,
        margem_m,
        largura - 2 * margem_m,
        altura - 2 * margem_m,
        6,
        stroke=1,
        fill=0,
    )

    # 3. Filete lateral esquerdo em gradiente verde (#163A28 -> #7BB661)
    passos = 36
    y_ini = margem_m + 6
    altura_util = (altura - 2 * margem_m) - 12
    passo_h = altura_util / passos
    r1, g1, b1 = (0x16 / 255.0, 0x3A / 255.0, 0x28 / 255.0)
    r2, g2, b2 = (0x7B / 255.0, 0xB6 / 255.0, 0x61 / 255.0)
    for idx in range(passos):
        t = idx / float(max(passos - 1, 1))
        cor_passo = colors.Color(
            r2 + (r1 - r2) * t,
            g2 + (g1 - g2) * t,
            b2 + (b1 - b2) * t,
        )
        canvas.setFillColor(cor_passo)
        canvas.rect(
            margem_m,
            y_ini + idx * passo_h,
            4.2,
            passo_h + 0.4,
            stroke=0,
            fill=1,
        )

    # 4. Barra superior verde-floresta (6pt) + filete verde-folha (2pt)
    canvas.setFillColor(COR_PRIMARIA)
    canvas.rect(
        margem_m, altura - margem_m - 6, largura - 2 * margem_m, 6,
        stroke=0, fill=1,
    )
    canvas.setFillColor(COR_ACENTO)
    canvas.rect(
        margem_m, altura - margem_m - 8, largura - 2 * margem_m, 2,
        stroke=0, fill=1,
    )

    # 5. Grafismos sutis de arcos concentricos nos cantos (anéis do emblema)
    canvas.setStrokeColor(COR_BORDA)
    canvas.setLineWidth(0.55)
    for raio in (22, 30, 38):
        canvas.arc(
            largura - margem_m - raio,
            altura - margem_m - raio,
            largura - margem_m + raio,
            altura - margem_m + raio,
            180,
            90,
        )
    for raio in (36, 48, 60):
        canvas.arc(
            largura - margem_m - raio,
            margem_m - raio,
            largura - margem_m + raio,
            margem_m + raio,
            90,
            90,
        )
    canvas.setStrokeColor(COR_ACENTO)
    canvas.setLineWidth(0.8)
    canvas.arc(
        largura - margem_m - 26,
        altura - margem_m - 26,
        largura - margem_m + 26,
        altura - margem_m + 26,
        195,
        60,
    )

    # 6. Cabecalho Timbrado: Logo a esquerda + Titulo e Pilula a direita
    y_topo = altura - 104
    logo = _carregar_imagem("logo-agrotracer-full.png")
    if logo is not None:
        canvas.drawImage(
            logo, 44, y_topo, width=76, height=65, mask="auto",
        )

    x_dir = largura - 44
    canvas.setFillColor(COR_PRIMARIA)
    canvas.setFont("Helvetica-Bold", 17)
    canvas.drawRightString(
        x_dir, altura - 56, "CERTIFICADO DE EMISSÕES", charSpace=1.4,
    )

    canvas.setFillColor(COR_SECUNDARIA)
    canvas.setFont("Helvetica", 9.5)
    canvas.drawRightString(
        x_dir,
        altura - 71,
        "Rastreabilidade Bovina & Pegada de Carbono • AgroTracer ESG",
    )

    # Pilula Registro {id} | Lote {lote_id}
    texto_pilula = (
        f"Registro #{certificado.id}   |   Lote #{certificado.lote_id}"
        f"   |   Status: {getattr(certificado, 'status', 'VALIDO')}"
    )
    canvas.setFont("Helvetica-Bold", 8.5)
    larg_pilula = canvas.stringWidth(texto_pilula, "Helvetica-Bold", 8.5) + 22
    x_pilula = x_dir - larg_pilula
    y_pilula = altura - 95
    canvas.setFillColor(COR_CARD)
    canvas.setStrokeColor(COR_SECUNDARIA)
    canvas.setLineWidth(0.8)
    canvas.roundRect(
        x_pilula, y_pilula, larg_pilula, 17, 8.5, stroke=1, fill=1,
    )
    canvas.setFillColor(COR_PRIMARIA)
    canvas.drawString(x_pilula + 11, y_pilula + 5, texto_pilula)

    # Linha divisoria do cabecalho
    canvas.setStrokeColor(COR_SECUNDARIA)
    canvas.setLineWidth(1.1)
    canvas.line(44, altura - 114, largura - 44, altura - 114)
    canvas.setStrokeColor(COR_ACENTO)
    canvas.setLineWidth(2.2)
    canvas.line(44, altura - 114, 134, altura - 114)

    # 7. Linha final de rodape institucional timbrado
    y_rodape = 36
    canvas.setStrokeColor(COR_BORDA)
    canvas.setLineWidth(0.7)
    canvas.line(44, y_rodape + 14, largura - 44, y_rodape + 14)

    canvas.setFillColor(COR_PRIMARIA)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(
        44, y_rodape, "AGROTRACER • Documento Eletrônico Verificável",
    )
    canvas.setFillColor(COR_LABEL)
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(
        x_dir,
        y_rodape,
        f"Referência do Ciclo: {data_ref} • Schema Canônico v1",
    )
    canvas.restoreState()


def _criar_estilos():
    estilos = getSampleStyleSheet()
    estilos.add(ParagraphStyle(
        "SecaoTitulo",
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=COR_PRIMARIA,
        spaceBefore=6,
        spaceAfter=6,
    ))
    estilos.add(ParagraphStyle(
        "AlertaSintetico",
        fontName="Helvetica",
        fontSize=8.8,
        leading=12.5,
        textColor=COR_ALERTA_TXT,
    ))
    estilos.add(ParagraphStyle(
        "KpiLabel",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10.5,
        textColor=COR_LABEL,
    ))
    estilos.add(ParagraphStyle(
        "KpiValorPrimario",
        fontName="Helvetica-Bold",
        fontSize=16.5,
        leading=20,
        textColor=COR_PRIMARIA,
        spaceBefore=3,
        spaceAfter=2,
    ))
    estilos.add(ParagraphStyle(
        "KpiValorSecundario",
        fontName="Helvetica-Bold",
        fontSize=16.5,
        leading=20,
        textColor=COR_SECUNDARIA,
        spaceBefore=3,
        spaceAfter=2,
    ))
    estilos.add(ParagraphStyle(
        "KpiValorNeutro",
        fontName="Helvetica-Bold",
        fontSize=15.5,
        leading=20,
        textColor=COR_GRAFITE,
        spaceBefore=3,
        spaceAfter=2,
    ))
    estilos.add(ParagraphStyle(
        "KpiSub",
        fontName="Helvetica",
        fontSize=7.8,
        leading=10.5,
        textColor=COR_LABEL,
    ))
    estilos.add(ParagraphStyle(
        "TabelaLabel",
        fontName="Helvetica-Bold",
        fontSize=8.8,
        leading=12,
        textColor=COR_LABEL,
    ))
    estilos.add(ParagraphStyle(
        "TabelaValor",
        fontName="Helvetica-Bold",
        fontSize=9.2,
        leading=12.5,
        textColor=COR_GRAFITE,
    ))
    estilos.add(ParagraphStyle(
        "TabelaValorMono",
        fontName="Courier-Bold",
        fontSize=9.2,
        leading=12.5,
        textColor=COR_PRIMARIA,
        wordWrap="CJK",
    ))
    estilos.add(ParagraphStyle(
        "IntegridadeCabecalho",
        fontName="Helvetica-Bold",
        fontSize=8.8,
        leading=12,
        textColor=COR_SECUNDARIA,
    ))
    estilos.add(ParagraphStyle(
        "DigestMono",
        fontName="Courier-Bold",
        fontSize=8.8,
        leading=12,
        textColor=COR_PRIMARIA,
    ))
    estilos.add(ParagraphStyle(
        "AvisoLegal",
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=COR_LABEL,
    ))
    return estilos


def _montar_card_kpi(
    titulo: str,
    valor_principal: str,
    subtitulo: str,
    estilo_valor: ParagraphStyle,
    cor_topo,
    estilos,
) -> Table:
    conteudo = [
        [Paragraph(escape(titulo), estilos["KpiLabel"])],
        [Paragraph(escape(valor_principal), estilo_valor)],
        [Paragraph(escape(subtitulo), estilos["KpiSub"])],
    ]
    card = Table(conteudo, colWidths=[246])
    card.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COR_CARD),
        ("BOX", (0, 0), (-1, -1), 0.8, COR_BORDA),
        ("LINEABOVE", (0, 0), (-1, 0), 3.0, cor_topo),
        ("LEFTPADDING", (0, 0), (-1, -1), 13),
        ("RIGHTPADDING", (0, 0), (-1, -1), 13),
        ("TOPPADDING", (0, 0), (0, 0), 10),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 10),
        ("TOPPADDING", (0, 1), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -2), 1),
    ]))
    return card


def renderizar_pdf(certificado, snapshot):
    if sha256_json(conteudo_snapshot(snapshot)) != certificado.snapshot_sha256:
        raise ErroFechamento(
            409, "SNAPSHOT_INTEGRO_OBRIGATORIO",
            "Snapshot nao corresponde ao certificado.",
        )

    estilos = _criar_estilos()
    saida = BytesIO()
    documento = SimpleDocTemplate(
        saida,
        pagesize=A4,
        rightMargin=44,
        leftMargin=44,
        topMargin=126,
        bottomMargin=56,
        title="Certificado de Emissões AgroTracer",
        author="AgroTracer",
    )

    tipos = sorted({
        origem["source_type"]
        for periodo in snapshot.entradas["periodos"]
        for origem in periodo["proveniencia"]
    })
    tipos_str = ", ".join(tipos)

    emissao_bruta = snapshot.resultados["emissao_total_kg_co2e"]
    intensidade_bruta = snapshot.resultados["intensidade_kg_co2e_kg"]
    data_abate_iso = str(snapshot.entradas["data_abate"])
    data_abate_br = _formatar_data_br(data_abate_iso)
    num_animais = int(snapshot.entradas["numero_animais_abate"])
    rotulo_animais = (
        f"{num_animais} animal"
        if num_animais == 1
        else f"{num_animais} animais"
    )

    emissao_fmt = f"{_formatar_decimal_br(emissao_bruta, 2, 2)} kg CO2e"
    intensidade_fmt = (
        f"{_formatar_decimal_br(intensidade_bruta, 4, 4)} kg CO2e / kg carcaça"
    )

    itens = []

    # 1. Faixa condicional de aviso SYNTHETIC em âmbar
    if "SYNTHETIC" in tipos:
        texto_alerta = (
            "<b>[ ! ] SYNTHETIC — DEMONSTRAÇÃO DIDÁTICA:</b> "
            "Contém fatores sintéticos. Não representa validação científica "
            "ou certificação ambiental independente."
        )
        banner = Table(
            [[Paragraph(texto_alerta, estilos["AlertaSintetico"])]],
            colWidths=[507],
        )
        banner.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), COR_ALERTA_BG),
            ("BOX", (0, 0), (-1, -1), 0.9, COR_ALERTA_BORDA),
            ("LINEBEFORE", (0, 0), (0, -1), 3.5, COR_ALERTA_BORDA),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        itens.append(banner)
        itens.append(Spacer(1, 12))

    # 2. Bloco Principal — Resultados do Snapshot (Grid 2x2 de KPIs)
    itens.append(Paragraph(
        "RESULTADOS DO SNAPSHOT CONSOLIDADO", estilos["SecaoTitulo"],
    ))

    card_emissao = _montar_card_kpi(
        "EMISSÃO TOTAL (kg CO2e)",
        emissao_fmt,
        "Pegada total estimada no ciclo zootécnico",
        estilos["KpiValorPrimario"],
        COR_PRIMARIA,
        estilos,
    )
    card_intensidade = _montar_card_kpi(
        "INTENSIDADE DE CARBONO",
        intensidade_fmt,
        "Emissão relativa por quilograma de carcaça",
        estilos["KpiValorSecundario"],
        COR_SECUNDARIA,
        estilos,
    )
    card_data = _montar_card_kpi(
        "DATA DE ABATE",
        data_abate_br,
        f"Data de encerramento do lote (ISO: {data_abate_iso})",
        estilos["KpiValorNeutro"],
        COR_ACENTO,
        estilos,
    )
    card_animais = _montar_card_kpi(
        "ANIMAIS NO ABATE",
        rotulo_animais,
        "Cabeças apuradas no fechamento do manejo",
        estilos["KpiValorNeutro"],
        COR_ACENTO,
        estilos,
    )

    grid_kpis = Table(
        [
            [card_emissao, card_intensidade],
            [card_data, card_animais],
        ],
        colWidths=[249, 249],
        spaceBefore=2,
        spaceAfter=14,
    )
    grid_kpis.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 0),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    itens.append(grid_kpis)

    # 3. Bloco Secundário — Método e Proveniência
    itens.append(Paragraph(
        "MÉTODO E PROVENIÊNCIA TÉCNICA", estilos["SecaoTitulo"],
    ))

    linhas_metodo = [
        [
            Paragraph("Versão do método", estilos["TabelaLabel"]),
            Paragraph(
                escape(str(snapshot.versao_metodo)),
                estilos["TabelaValorMono"],
            ),
        ],
        [
            Paragraph("Versão dos parâmetros", estilos["TabelaLabel"]),
            Paragraph(
                escape(str(snapshot.versao_parametros)),
                estilos["TabelaValorMono"],
            ),
        ],
        [
            Paragraph("Tipo de fonte (source_type)", estilos["TabelaLabel"]),
            Paragraph(escape(tipos_str), estilos["TabelaValor"]),
        ],
        [
            Paragraph("Identificação do registro", estilos["TabelaLabel"]),
            Paragraph(
                f"Certificado #{certificado.id} vinculado ao Lote "
                f"#{certificado.lote_id} (Snapshot #{snapshot.id})",
                estilos["TabelaValor"],
            ),
        ],
    ]
    tabela_metodo = Table(
        linhas_metodo, colWidths=[175, 332], spaceBefore=2, spaceAfter=16,
    )
    tabela_metodo.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COR_CARD),
        ("BACKGROUND", (0, 2), (-1, 2), COR_CARD),
        ("BOX", (0, 0), (-1, -1), 0.8, COR_BORDA),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, COR_BORDA),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    itens.append(tabela_metodo)

    # 4. Rodapé Timbrado — Integridade e Verificação Criptográfica
    itens.append(HRFlowable(
        width="100%", thickness=1.0, color=COR_SECUNDARIA,
        spaceBefore=2, spaceAfter=10,
    ))
    itens.append(Paragraph(
        "INTEGRIDADE E VERIFICAÇÃO CRIPTOGRÁFICA", estilos["SecaoTitulo"],
    ))

    caixa_hash = Table(
        [
            [Paragraph(
                "[ SELO DE INTEGRIDADE ]  snapshot_sha256 — "
                "SHA-256 do snapshot canônico (schema 1)",
                estilos["IntegridadeCabecalho"],
            )],
            [Paragraph(
                escape(str(certificado.snapshot_sha256)),
                estilos["DigestMono"],
            )],
        ],
        colWidths=[507],
        spaceBefore=2,
        spaceAfter=8,
    )
    caixa_hash.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COR_CARD),
        ("BOX", (0, 0), (-1, -1), 0.9, COR_BORDA),
        ("LINEBEFORE", (0, 0), (0, -1), 3.5, COR_SECUNDARIA),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (0, 0), 8),
        ("BOTTOMPADDING", (0, 0), (0, 0), 2),
        ("TOPPADDING", (0, 1), (0, 1), 2),
        ("BOTTOMPADDING", (0, 1), (0, 1), 8),
    ]))
    itens.append(caixa_hash)

    itens.append(Paragraph(
        "Documento gerado a partir do registro imutável. O hash do arquivo "
        "PDF é armazenado separadamente após a geração.",
        estilos["AvisoLegal"],
    ))

    desenhar_pagina = partial(
        _desenhar_papel_timbrado, certificado, data_abate_br,
    )
    documento.build(
        itens,
        onFirstPage=desenhar_pagina,
        onLaterPages=desenhar_pagina,
        canvasmaker=partial(Canvas, invariant=1),
    )
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
