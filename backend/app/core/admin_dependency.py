"""Autorizacao administrativa para operacoes de parametros."""

import os

from fastapi import Depends

from app.core.bridge_dependency import exigir_usuario_wordpress
from app.core.bridge_errors import ErroBridge


def obter_ids_administradores() -> set[int]:
    configuracao = os.getenv(
        "AGROTRACER_ADMIN_WP_IDS",
        "",
    )

    if not configuracao.strip():
        raise ErroBridge(
            503,
            "ADMIN_CONFIG_UNAVAILABLE",
            "Autorizacao administrativa indisponivel.",
        )

    valores = [
        item.strip()
        for item in configuracao.split(",")
    ]

    if any(
        not valor.isdecimal() or int(valor) <= 0
        for valor in valores
    ):
        raise ErroBridge(
            503,
            "ADMIN_CONFIG_INVALID",
            "Configuracao administrativa invalida.",
        )

    return {int(valor) for valor in valores}


async def exigir_admin_wordpress(
    wp_user_id: int = Depends(exigir_usuario_wordpress),
) -> int:
    administradores = obter_ids_administradores()

    if wp_user_id not in administradores:
        raise ErroBridge(
            403,
            "ADMIN_REQUIRED",
            "Esta operacao exige permissao administrativa.",
        )

    return wp_user_id
