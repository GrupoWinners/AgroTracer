"""S5-T05: DTO estritamente minimizado para consulta publica (RN-13)."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class CertificadoPublicoResultados(BaseModel):
    model_config = ConfigDict(extra="forbid")

    emissao_total_kg_co2e: str
    intensidade_kg_co2e_kg: str
    unidade_emissao: str = "kg CO2e"
    unidade_intensidade: str = "kg CO2e/kg de carcaça"


class CertificadoPublicoSaida(BaseModel):
    model_config = ConfigDict(extra="forbid")

    certificado_id: int
    lote_id: int
    status: Literal["VALIDO", "REVOGADO"]
    emitido_em: datetime
    versao_metodo: str
    versao_parametros: str
    source_types: list[str]
    synthetic: bool
    aviso_proveniencia: str | None = None
    data_abate: str
    numero_animais_abate: int
    resultados: CertificadoPublicoResultados
    snapshot_sha256: str
    pdf_sha256: str | None = None
