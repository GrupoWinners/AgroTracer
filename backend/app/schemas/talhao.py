from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class TalhaoBase(BaseModel):
    identificador: str = Field(..., min_length=1, max_length=50)
    area_hectares: Decimal = Field(..., gt=0)


class TalhaoCreate(TalhaoBase):
    pass


class TalhaoResponse(TalhaoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fazenda_id: int
