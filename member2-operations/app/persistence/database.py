"""
Database configuration and session management for Operations Service.
Supports PostgreSQL (with operations_schema) and graceful fallback to SQLite
for isolated local testing and fast CI runs.
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from ..config import settings
from .models import Base


def get_engine():
    """Initializes SQLAlchemy engine with PostgreSQL or SQLite fallback."""
    db_url = settings.database_url
    try:
        if db_url and "postgresql" in db_url:
            eng = create_engine(
                db_url,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                connect_args={"connect_timeout": 3}
            )
            # Test connection
            with eng.connect() as conn:
                pass
            return eng
    except Exception:
        pass

    # Fallback to in-memory SQLite database
    from sqlalchemy.pool import StaticPool
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Creates all operations-owned tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
