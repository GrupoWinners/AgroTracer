from pydantic import BaseModel, ConfigDict, Field


class FazendaBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=120)
    municipio: str = Field(..., min_length=1, max_length=80)
    uf: str = Field(..., min_length=2, max_length=2)
    numero_car_informado: str | None = Field(None, max_length=100)


class FazendaCreate(FazendaBase):
    pass


class FazendaUpdate(BaseModel):
    nome: str | None = Field(None, min_length=1, max_length=120)
    municipio: str | None = Field(None, min_length=1, max_length=80)
    uf: str | None = Field(None, min_length=2, max_length=2)
    numero_car_informado: str | None = Field(None, max_length=100)


class FazendaResponse(FazendaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    produtor_id: int
