from datetime import datetime

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class MovimentacaoCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    animal_id: int | None = Field(default=None, gt=0)
    lote_id: int | None = Field(default=None, gt=0)

    origem_talhao_id: int | None = Field(default=None, gt=0)
    destino_talhao_id: int | None = Field(default=None, gt=0)

    tipo: str = Field(min_length=1, max_length=30)
    data_hora: AwareDatetime

    observacao: str | None = Field(
        default=None,
        max_length=500,
    )

    @model_validator(mode="after")
    def validar_alvo_e_trajeto(self):
        if (self.animal_id is None) == (self.lote_id is None):
            raise ValueError(
                "Informe exatamente um alvo: animal_id ou lote_id."
            )

        if (
            self.origem_talhao_id is not None
            and self.destino_talhao_id is not None
            and self.origem_talhao_id == self.destino_talhao_id
        ):
            raise ValueError(
                "Origem e destino nao podem ser iguais."
            )

        return self


class MovimentacaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    animal_id: int | None
    lote_id: int | None
    origem_talhao_id: int | None
    destino_talhao_id: int | None
    tipo: str
    data_hora: datetime
    observacao: str | None
