import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

import app.models  # noqa: F401
from app.models.base import Base

# Configuração de logs do Alembic
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def get_url():
    """Garante a leitura da variável DATABASE_URL no ambiente."""
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("A variável DATABASE_URL não está configurada no ambiente.")
    return url


def run_migrations_offline():
    """Execução de migrations no modo Offline (Gera scripts SQL diretamente)."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Callback síncrono para execução das migrations dentro da conexão assíncrona."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    """Cria a engine assíncrona com asyncpg e executa as migrations no loop de eventos."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online():
    """Ponto de entrada online utilizando o executor assíncrono."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()