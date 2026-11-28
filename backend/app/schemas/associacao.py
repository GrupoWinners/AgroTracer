from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AssociacaoCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    animal_id: int = Field(..., gt=0)


class AssociacaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    animal_id: int
    lote_id: int
    associado_em: datetime
    desassociado_em: datetime | None
