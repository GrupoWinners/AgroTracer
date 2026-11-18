"""Download privado do PDF, protegido por HMAC e proprietario."""

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.fechamentos import _erro
from app.core.bridge_dependency import exigir_usuario_wordpress
from app.core.bridge_openapi import BRIDGE_OPENAPI
from app.core.validation_route import ValidationRoute
from app.db.database import obter_db
from app.models.certificado import Certificado
from app.models.fazenda import Fazenda
from app.models.lote import Lote
from app.models.produtor import Produtor
from app.models.snapshot_fechamento import SnapshotFechamento
from app.services.certificado_pdf_service import obter_pdf
from app.services.fechamento_service import ErroFechamento


router = APIRouter(tags=["Certificados"], route_class=ValidationRoute)


@router.get(
    "/certificados/{certificado_id}/pdf", response_class=Response,
    openapi_extra=BRIDGE_OPENAPI,
    responses={
        200: {"content": {"application/pdf": {}},
              "description": "PDF; X-PDF-SHA256 contem hash dos bytes"},
        401: {"description": "HMAC invalido"},
        403: {"description": "Usuario obrigatorio"},
        404: {"description": "Certificado inexistente ou nao autorizado"},
        409: {"description": "Snapshot ou PDF sem integridade"},
        503: {"description": "Geracao temporariamente indisponivel"},
    },
)
def baixar_pdf(
    certificado_id: int, request: Request,
    usuario: int = Depends(exigir_usuario_wordpress),
    db: Session = Depends(obter_db),
):
    try:
        certificado = db.scalar(
            select(Certificado)
            .join(Lote, Certificado.lote_id == Lote.id)
            .join(Fazenda, Lote.fazenda_id == Fazenda.id)
            .join(Produtor, Fazenda.produtor_id == Produtor.id)
            .where(Certificado.id == certificado_id,
                   Produtor.wordpress_user_id == usuario)
            .with_for_update(of=Certificado)
        )
        if certificado is None:
            raise ErroFechamento(
                404, "CERTIFICADO_NAO_ENCONTRADO",
                "Certificado nao encontrado.",
            )
        snapshot = db.get(SnapshotFechamento, certificado.snapshot_id)
        arquivo = obter_pdf(db, certificado, snapshot)
        resposta = Response(
            content=arquivo.conteudo, media_type="application/pdf",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="certificado-{certificado.id}.pdf"'
                ),
                "X-PDF-SHA256": arquivo.pdf_sha256,
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
            },
        )
        db.commit()
        return resposta
    except ErroFechamento as erro:
        db.rollback()
        return _erro(request, erro.status_code, erro.codigo, erro.mensagem)
    except Exception:
        db.rollback()
        return _erro(
            request, 503, "PDF_INDISPONIVEL",
            "PDF temporariamente indisponivel. Tente novamente.",
        )
