"""Contrato de fechamento com Decimal e validacao estrita."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FechamentoEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    data_abate: date
    numero_animais_abate: int = Field(strict=True, gt=0)
    peso_medio_abate_kg: Decimal = Field(gt=0)
    rendimento_carcaca: Decimal = Field(gt=0, le=1)

    @field_validator("data_abate", mode="before")
    @classmethod
    def data_iso_obrigatoria(cls, valor):
        if not isinstance(valor, str) or len(valor) != 10:
            raise ValueError("Use data AAAA-MM-DD.")
        return valor

    @field_validator("peso_medio_abate_kg", "rendimento_carcaca",
                     mode="before")
    @classmethod
    def decimal_sem_float(cls, valor):
        if isinstance(valor, (bool, float)):
            raise ValueError("Envie Decimal como string ou inteiro.")
        return valor


class FechamentoSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lote_id: int
    status_lote: str
    data_abate: date
    numero_animais_abate: int
    parametro_set_id: int
    versao_metodo: str
    emissao_total_kg_co2e: str
    intensidade_kg_co2e_kg: str
