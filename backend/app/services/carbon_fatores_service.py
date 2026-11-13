"""S4-T01: recuperacao explicita de fatores de uma versao historica."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.fator import Fator
from app.models.parametro_set import ParametroSet
from app.services.carbon_engine import ErroCarbono, FatoresVersionados


UNIDADE_EMISSAO = "kg CO2e/cabeca/dia"
UNIDADES_MULTIPLICADOR = {"1", "adimensional"}
MULTIPLICADORES = ("K_IDADE", "K_PASTAGEM", "K_SUPLEMENTACAO")


def carregar_fatores_versionados(
    db: Session,
    parametro_set_id: int,
    tipo_dieta: str,
) -> FatoresVersionados:
    """FE_BASE_DIETA:<DIETA> e tres multiplicadores sem defaults magicos."""
    if type(parametro_set_id) is not int or parametro_set_id <= 0:
        raise ErroCarbono("Conjunto de parametros invalido.")
    if not isinstance(tipo_dieta, str) or not tipo_dieta.strip():
        raise ErroCarbono("Tipo de dieta invalido.")

    conjunto = db.get(ParametroSet, parametro_set_id)
    if conjunto is None:
        raise ErroCarbono("Conjunto de parametros nao encontrado.")

    chaves = (f"FE_BASE_DIETA:{tipo_dieta.strip().upper()}",) + (
        MULTIPLICADORES
    )
    fatores = db.scalars(
        select(Fator).where(
            Fator.parametro_set_id == parametro_set_id,
            Fator.chave.in_(chaves),
        )
    ).all()
    por_chave = {item.chave: item for item in fatores}
    if set(chaves) != set(por_chave):
        raise ErroCarbono(
            "Fatores incompletos para a dieta e versao informadas."
        )
    if por_chave[chaves[0]].unidade != UNIDADE_EMISSAO:
        raise ErroCarbono("Unidade do fator de emissao incompativel.")
    if any(
        por_chave[chave].unidade.lower() not in UNIDADES_MULTIPLICADOR
        for chave in MULTIPLICADORES
    ):
        raise ErroCarbono("Multiplicadores devem ser adimensionais.")

    for fator in fatores:
        if fator.source_type != "SYNTHETIC" and not fator.source_uri:
            raise ErroCarbono("Fator nao sintetico sem fonte rastreavel.")

    return FatoresVersionados(
        parametro_set_id=conjunto.id,
        versao=conjunto.versao,
        fe_base_dieta=por_chave[chaves[0]].valor,
        k_idade=por_chave["K_IDADE"].valor,
        k_pastagem=por_chave["K_PASTAGEM"].valor,
        k_suplementacao=por_chave["K_SUPLEMENTACAO"].valor,
        proveniencia=tuple(
            (chave, por_chave[chave].source_type,
             por_chave[chave].source_uri or "",
             por_chave[chave].unidade)
            for chave in chaves
        ),
    )
