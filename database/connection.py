"""
Database connection management using SQLAlchemy.
Supports PostgreSQL (production) and SQLite (testing).
"""
from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from database.schema import Base
from models.config import get_settings

logger = logging.getLogger(__name__)

# Module-level engine and session factory (lazy init)
_engine: Optional[Engine] = None
_session_factory: Optional[sessionmaker] = None


def get_engine(database_url: Optional[str] = None) -> Engine:
    """
    Get or create the SQLAlchemy engine.
    Uses the provided URL or falls back to settings.
    """
    global _engine
    if _engine is None or database_url is not None:
        url = database_url or get_settings().database_url
        # Determine connect args based on dialect
        connect_args = {}
        if url.startswith("sqlite"):
            connect_args["check_same_thread"] = False

        _engine = create_engine(
            url,
            echo=False,
            pool_pre_ping=True,
            connect_args=connect_args,
        )
        logger.info("Database engine created for: %s", _mask_url(url))
    return _engine


def get_session_factory(engine: Optional[Engine] = None) -> sessionmaker:
    """Get or create the session factory."""
    global _session_factory
    if _session_factory is None or engine is not None:
        eng = engine or get_engine()
        _session_factory = sessionmaker(bind=eng, expire_on_commit=False)
    return _session_factory


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Context manager that provides a transactional database session.
    Commits on success, rolls back on exception.
    """
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_database(database_url: Optional[str] = None) -> None:
    """
    Initialise the database: create all tables.
    Used for fresh setups and testing.
    """
    engine = get_engine(database_url)
    Base.metadata.create_all(engine)
    logger.info("Database tables created successfully.")


def drop_database(database_url: Optional[str] = None) -> None:
    """
    Drop all database tables.
    WARNING: Destructive operation — use only in development/testing.
    """
    engine = get_engine(database_url)
    Base.metadata.drop_all(engine)
    logger.info("Database tables dropped.")


def check_connection(database_url: Optional[str] = None) -> dict:
    """
    Check database connectivity and return status info.
    Does NOT expose connection strings in the result.
    """
    try:
        engine = get_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()

            # Try to get server version
            try:
                ver = conn.execute(text("SELECT version()")).fetchone()
                server_version = ver[0] if ver else "Unknown"
            except Exception:
                server_version = "Connected (version query not supported)"

        return {
            "status": "connected",
            "server_version": server_version,
            "dialect": engine.dialect.name,
        }
    except Exception as e:
        logger.error("Database connection check failed: %s", str(e))
        return {
            "status": "disconnected",
            "error": _safe_error_message(str(e)),
        }


def reset_engine() -> None:
    """Reset the module-level engine. Used in testing."""
    global _engine, _session_factory
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _session_factory = None


def _mask_url(url: str) -> str:
    """Mask password in database URL for safe logging."""
    if "@" in url and ":" in url:
        try:
            prefix, rest = url.split("://", 1)
            if "@" in rest:
                creds, host = rest.split("@", 1)
                user = creds.split(":")[0] if ":" in creds else creds
                return f"{prefix}://{user}:****@{host}"
        except Exception:
            pass
    return url


def _safe_error_message(error: str) -> str:
    """Remove sensitive information from error messages."""
    # Strip potential connection string fragments
    import re
    # Remove anything that looks like a password in a connection string
    sanitised = re.sub(r"password=\S+", "password=****", error, flags=re.IGNORECASE)
    sanitised = re.sub(r"://\w+:\S+@", "://****:****@", sanitised)
    return sanitised
