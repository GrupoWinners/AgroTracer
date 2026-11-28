from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ManejoCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    inicio: date
    fim: date
    parametro_set_id: int = Field(gt=0, strict=True)
    tipo_dieta: str = Field(min_length=1, max_length=50)

    @field_validator("inicio", "fim", mode="before")
    @classmethod
    def exigir_data_iso(cls, valor):
        # Evita aceitar timestamp numérico ou datetime como data de manejo.
        if not isinstance(valor, str) or len(valor) != 10:
            raise ValueError("Use uma data no formato AAAA-MM-DD.")
        return valor


class ManejoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lote_id: int
    inicio: date
    fim: date
    parametro_set_id: int
    tipo_dieta: str
