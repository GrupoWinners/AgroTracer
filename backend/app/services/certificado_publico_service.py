"""S5-T05: consulta publica de certificado por token opaco (RN-13)."""

import ipaddress
import os

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.bridge_errors import ErroBridge
from app.models.certificado import Certificado
from app.models.certificado_pdf import CertificadoPDF
from app.models.snapshot_fechamento import SnapshotFechamento
from app.schemas.certificado_publico import (
    CertificadoPublicoResultados,
    CertificadoPublicoSaida,
)
from app.services.certificacao_service import conteudo_snapshot, sha256_json
from app.services.token_service import consultar_token

AVISO_SYNTHETIC = (
    "SYNTHETIC - DEMONSTRAÇÃO DIDÁTICA. "
    "Contém fatores sintéticos. Não representa validação científica "
    "ou certificação ambiental independente."
)


def _redes_proxies_confiaveis() -> list[
    ipaddress.IPv4Network | ipaddress.IPv6Network
]:
    bruto = os.environ.get("AGROTRACER_TRUSTED_PROXIES", "")
    redes = []
    for item in bruto.split(","):
        candidato = item.strip()
        if not candidato:
            continue
        try:
            rede = ipaddress.ip_network(candidato, strict=False)
            if rede.prefixlen == 0:
                raise ValueError("Proxy irrestrito")
            redes.append(rede)
        except ValueError:
            raise ErroBridge(
                503, "PROXY_CONFIG_INVALID",
                "Configuracao de proxy indisponivel.",
            ) from None
    return redes


def obter_ip_cliente(request: Request) -> str:
    """Resolve IP real apenas quando proxy confiavel estiver configurado."""
    peer_host = request.client.host if request.client else ""
    redes = _redes_proxies_confiaveis()
    if not redes or not peer_host:
        return peer_host or "desconhecido"

    try:
        peer_ip = ipaddress.ip_address(peer_host)
    except ValueError:
        return peer_host

    if not any(peer_ip in rede for rede in redes):
        return peer_host

    forwarded = request.headers.get("X-Forwarded-For", "")
    cadeia = [p.strip() for p in forwarded.split(",") if p.strip()]
    for candidato in reversed(cadeia):
        try:
            ip = ipaddress.ip_address(candidato)
        except ValueError:
            continue
        if not any(ip in rede for rede in redes):
            return str(ip)
    return peer_host


def montar_dto_publico(
    certificado: Certificado,
    snapshot: SnapshotFechamento,
    pdf_sha256: str | None = None,
) -> CertificadoPublicoSaida:
    """Constroi DTO publico por allowlist estrita, sem PII ou ORM."""
    if sha256_json(conteudo_snapshot(snapshot)) != certificado.snapshot_sha256:
        raise ErroBridge(
            409,
            "SNAPSHOT_INTEGRO_OBRIGATORIO",
            "Integridade do certificado comprometida.",
        )

    periodos = snapshot.entradas.get("periodos", [])
    source_types = sorted({
        origem["source_type"]
        for periodo in periodos
        for origem in periodo.get("proveniencia", [])
        if isinstance(origem, dict) and "source_type" in origem
    })
    synthetic = "SYNTHETIC" in source_types

    return CertificadoPublicoSaida(
        certificado_id=certificado.id,
        lote_id=certificado.lote_id,
        status=certificado.status,
        emitido_em=certificado.criado_em,
        versao_metodo=snapshot.versao_metodo,
        versao_parametros=snapshot.versao_parametros,
        source_types=source_types,
        synthetic=synthetic,
        aviso_proveniencia=AVISO_SYNTHETIC if synthetic else None,
        data_abate=str(snapshot.entradas["data_abate"]),
        numero_animais_abate=int(snapshot.entradas["numero_animais_abate"]),
        resultados=CertificadoPublicoResultados(
            emissao_total_kg_co2e=str(
                snapshot.resultados["emissao_total_kg_co2e"]
            ),
            intensidade_kg_co2e_kg=str(
                snapshot.resultados["intensidade_kg_co2e_kg"]
            ),
        ),
        snapshot_sha256=certificado.snapshot_sha256,
        pdf_sha256=pdf_sha256,
    )


async def consultar_certificado_publico(
    db: Session,
    redis,
    token: str,
    endereco_cliente: str,
) -> CertificadoPublicoSaida:
    """Consulta token opaco com rate limit e retorna DTO minimizado."""
    registro = await consultar_token(db, redis, token, endereco_cliente)
    certificado = db.scalar(
        select(Certificado).where(Certificado.token_id == registro.id)
    )
    if certificado is None:
        raise ErroBridge(
            404, "CERTIFICADO_NAO_ENCONTRADO", "Certificado nao encontrado."
        )
    snapshot = db.get(SnapshotFechamento, certificado.snapshot_id)
    if snapshot is None:
        raise ErroBridge(
            404, "CERTIFICADO_NAO_ENCONTRADO", "Certificado nao encontrado."
        )
    pdf_sha256 = db.scalar(
        select(CertificadoPDF.pdf_sha256).where(
            CertificadoPDF.certificado_id == certificado.id
        )
    )
    return montar_dto_publico(certificado, snapshot, pdf_sha256)
