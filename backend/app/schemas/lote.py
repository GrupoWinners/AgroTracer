from pydantic import BaseModel, ConfigDict, Field


class LoteCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    fazenda_id: int = Field(..., gt=0)

    codigo_lote: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )


class LoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fazenda_id: int
    codigo_lote: str
    status: str
