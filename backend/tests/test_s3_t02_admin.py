import pytest

from app.core.admin_dependency import (
    exigir_admin_wordpress,
    obter_ids_administradores,
)
from app.core.bridge_errors import ErroBridge


def test_carregar_administradores(monkeypatch):
    monkeypatch.setenv(
        "AGROTRACER_ADMIN_WP_IDS",
        "7, 42",
    )

    assert obter_ids_administradores() == {7, 42}


@pytest.mark.asyncio
async def test_permitir_administrador(monkeypatch):
    monkeypatch.setenv(
        "AGROTRACER_ADMIN_WP_IDS",
        "7,42",
    )

    resultado = await exigir_admin_wordpress(
        wp_user_id=42,
    )

    assert resultado == 42


@pytest.mark.asyncio
async def test_bloquear_usuario_comum(monkeypatch):
    monkeypatch.setenv(
        "AGROTRACER_ADMIN_WP_IDS",
        "7,42",
    )

    with pytest.raises(ErroBridge):
        await exigir_admin_wordpress(
            wp_user_id=99,
        )


def test_rejeitar_configuracao_ausente(monkeypatch):
    monkeypatch.delenv(
        "AGROTRACER_ADMIN_WP_IDS",
        raising=False,
    )

    with pytest.raises(ErroBridge):
        obter_ids_administradores()


@pytest.mark.parametrize(
    "configuracao",
    ["abc", "0", "-1", "1,abc", "1,"],
)
def test_rejeitar_configuracao_invalida(
    monkeypatch,
    configuracao,
):
    monkeypatch.setenv(
        "AGROTRACER_ADMIN_WP_IDS",
        configuracao,
    )

    with pytest.raises(ErroBridge):
        obter_ids_administradores()
