from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class AnimalCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    identificador: str = Field(
        ...,
        min_length=1,
        max_length=80,
    )

    rfid: str | None = Field(
        default=None,
        max_length=80,
    )

    data_nascimento_estimada: date | None = None


class AnimalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    produtor_id: int
    identificador: str
    rfid: str | None
    data_nascimento_estimada: date | None
