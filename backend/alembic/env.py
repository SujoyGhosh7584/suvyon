from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app.core.base import Base
from app.core.config import sqlalchemy_database_url

# Import ALL models — Alembic discovers tables only from imported models.
import app.models  # noqa: F401

# ----------------------------------------------------------
# Alembic Config
# ----------------------------------------------------------

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


# ----------------------------------------------------------
# Offline Migration
# ----------------------------------------------------------


def run_migrations_offline() -> None:
    url = sqlalchemy_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = sqlalchemy_database_url()
    connect_args = {"sslmode": "require"} if "supabase" in url else {}
    connectable = create_engine(url, poolclass=pool.NullPool, connect_args=connect_args)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
