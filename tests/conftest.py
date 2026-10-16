"""
Shared pytest fixtures for the Northstar Financial Planning & Forecasting Engine test suite.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Generator
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from database.schema import Base
from database.seed import seed_dimensions
from models.financial import AccountCategory, Favourability


@pytest.fixture(scope="session")
def test_engine():
    """Create an in-memory SQLite database engine for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    """Provide a transactional database session rolled back after each test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session_factory = sessionmaker(bind=connection, expire_on_commit=False)
    session = session_factory()

    # Seed dimensions into fresh session
    seed_dimensions(session)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def sample_variance_inputs():
    """Standard financial variance test cases."""
    return {
        "revenue_favourable": {
            "actual": Decimal("110000.00"),
            "budget": Decimal("100000.00"),
            "category": "revenue",
            "expected_variance": Decimal("10000.00"),
            "expected_pct": Decimal("10.00"),
            "expected_fav": Favourability.FAVOURABLE,
        },
        "expense_unfavourable": {
            "actual": Decimal("-55000.00"),
            "budget": Decimal("-50000.00"),
            "category": "expense",
            "expected_variance": Decimal("-5000.00"),
            "expected_pct": Decimal("10.00"),
            "expected_fav": Favourability.UNFAVOURABLE,
        },
        "profit_favourable": {
            "actual": Decimal("55000.00"),
            "budget": Decimal("50000.00"),
            "category": "profit",
            "expected_variance": Decimal("5000.00"),
            "expected_pct": Decimal("10.00"),
            "expected_fav": Favourability.FAVOURABLE,
        },
    }
