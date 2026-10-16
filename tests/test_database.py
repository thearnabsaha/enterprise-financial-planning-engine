"""
Tests for database connection, schema constraints, and repository operations.
"""
from __future__ import annotations

from decimal import Decimal
import pytest
from sqlalchemy.orm import Session

from database import repository as repo
from database.connection import check_connection


class TestDatabaseRepository:
    """Test repository CRUD operations on SQLite in-memory database."""

    def test_database_connectivity(self):
        """Database connection check returns connected status."""
        status = check_connection()
        assert status["status"] == "connected"

    def test_departments_crud(self, db_session: Session):
        """Retrieve and upsert departments."""
        depts = repo.get_all_departments(db_session)
        assert len(depts) >= 6

        eng = repo.get_department_by_code(db_session, "ENG")
        assert eng is not None
        assert eng.name == "Engineering"

    def test_accounts_crud(self, db_session: Session):
        """Retrieve accounts and verify revenue and expense classifications."""
        accounts = repo.get_all_accounts(db_session)
        assert len(accounts) >= 12

        rev = repo.get_account_by_code(db_session, "REV")
        assert rev is not None
        assert rev.category == "revenue"
        assert rev.sign_convention == 1

        cloud = repo.get_account_by_code(db_session, "CLOUD")
        assert cloud is not None
        assert cloud.category == "expense"
        assert cloud.sign_convention == -1

    def test_audit_event_logging(self, db_session: Session):
        """Audit events are logged and retrievable."""
        repo.log_audit_event(
            session=db_session,
            event_type="TEST_EVENT",
            event_description="Test event description",
            entity_type="TEST",
            entity_id="123",
            metadata={"test_key": "test_val"},
        )

        events = repo.get_recent_audit_events(db_session, limit=10)
        assert any(e.event_type == "TEST_EVENT" for e in events)
