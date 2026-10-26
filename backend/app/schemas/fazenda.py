from pydantic import BaseModel, ConfigDict, Field, model_validator


class FazendaBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=120)
    municipio: str = Field(..., min_length=1, max_length=80)
    uf: str = Field(..., min_length=2, max_length=2)
    numero_car_informado: str | None = Field(None, max_length=100)

    @model_validator(mode="before")
    @classmethod
    def traduzir_campos_legados(cls, data):
        if isinstance(data, dict):
            if "nome" not in data and "nome_propriedade" in data:
                data["nome"] = data["nome_propriedade"]
            if "numero_car_informado" not in data and "numero_car" in data:
                data["numero_car_informado"] = data["numero_car"]
        return data


class FazendaCreate(FazendaBase):
    pass


class FazendaUpdate(BaseModel):
    nome: str | None = Field(None, min_length=1, max_length=120)
    municipio: str | None = Field(None, min_length=1, max_length=80)
    uf: str | None = Field(None, min_length=2, max_length=2)
    numero_car_informado: str | None = Field(None, max_length=100)

    @model_validator(mode="before")
    @classmethod
    def traduzir_campos_legados(cls, data):
        if isinstance(data, dict):
            if "nome" not in data and "nome_propriedade" in data:
                data["nome"] = data["nome_propriedade"]
            if "numero_car_informado" not in data and "numero_car" in data:
                data["numero_car_informado"] = data["numero_car"]
        return data


class FazendaResponse(FazendaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    produtor_id: int
