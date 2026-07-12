from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from app.core.config import settings
from app.core.base import Base

# Import ALL models here.
# Alembic discovers tables only from imported models.
from app.models.user import User
from app.models.workspace import Workspace
from app.models.conversation import Conversation
from app.models.message import Message

# ----------------------------------------------------------
# Alembic Config
# ----------------------------------------------------------

config = context.config


if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# ----------------------------------------------------------
# Metadata for Autogenerate
# ----------------------------------------------------------

target_metadata = Base.metadata


# ----------------------------------------------------------
# Offline Migration
# ----------------------------------------------------------


def run_migrations_offline() -> None:
    """
    Run migrations without creating a database connection.
    """

    url = settings.DATABASE_URL

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# ----------------------------------------------------------
# Online Migration
# ----------------------------------------------------------


def run_migrations_online() -> None:
    """
    Run migrations using database connection.
    """

    connectable = engine_from_config(
        {"sqlalchemy.url": settings.DATABASE_URL},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


# ----------------------------------------------------------
# Entry Point
# ----------------------------------------------------------

if context.is_offline_mode():

    run_migrations_offline()

else:

    run_migrations_online()
