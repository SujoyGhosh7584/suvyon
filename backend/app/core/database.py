from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# ------------------------------------------------------------------
# Database Engine
# ------------------------------------------------------------------

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=1800,
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
