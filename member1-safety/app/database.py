"""Database connection, engine configuration, and session management."""

import logging
from typing import Generator
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from .config import settings

logger = logging.getLogger("safety.database")

# Attempt primary database connection (PostgreSQL) with SQLite fallback
_engine = None

def _create_configured_engine():
    global _engine
    primary_url = settings.database_url
    fallback_url = settings.sqlite_fallback_url

    try:
        # Test connecting to primary
        test_engine = create_engine(
            primary_url,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 3} if "postgresql" in primary_url else {},
        )
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(f"Connected to primary database: {primary_url.split('@')[-1]}")
        _engine = test_engine
    except Exception as e:
        if settings.sqlite_fallback:
            logger.warning(
                f"Primary database connection failed ({e}). Falling back to SQLite: {fallback_url}"
            )
            _engine = create_engine(
                fallback_url,
                connect_args={"check_same_thread": False} if "sqlite" in fallback_url else {},
            )
        else:
            raise e

    return _engine


engine = _create_configured_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    # Import db_models so Base metadata is populated
    from . import db_models  # noqa: F401

    try:
        # Create schema if postgresql
        if engine.dialect.name == "postgresql":
            with engine.connect() as conn:
                conn.execute(text("CREATE SCHEMA IF NOT EXISTS safety"))
                conn.commit()

        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        # In testing/demo mode, let in-memory services operate if DB init fails
        pass
