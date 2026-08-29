from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import sqlalchemy_database_url


_db_url = sqlalchemy_database_url()
_is_supabase = "supabase.co" in _db_url or "supabase.com" in _db_url
_is_pooler = ":6543" in _db_url
_connect_args = {"sslmode": "require"} if _is_supabase else {}

# ------------------------------------------------------------------
# Database Engine
# ------------------------------------------------------------------

if _is_pooler:
    engine = create_engine(
        _db_url,
        poolclass=NullPool,
        connect_args=_connect_args,
        future=True,
    )
else:
    engine = create_engine(
        _db_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
        pool_recycle=1800,
        connect_args=_connect_args,
        future=True,
    )


# ------------------------------------------------------------------
# Session Factory
# ------------------------------------------------------------------

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=Session,
)


# ------------------------------------------------------------------
# Dependency
# ------------------------------------------------------------------


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency.

    Provides a database session and guarantees
    that it is properly closed after use.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
