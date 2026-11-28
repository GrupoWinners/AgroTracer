"""Artefato binario e digest sao persistidos juntos apos geracao."""

from sqlalchemy import ForeignKey, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CertificadoPDF(Base):
    __tablename__ = "certificados_pdf"

    certificado_id: Mapped[int] = mapped_column(
        ForeignKey("certificados.id", ondelete="RESTRICT"), primary_key=True,
    )
    conteudo: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    pdf_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
