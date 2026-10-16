"""
Audit trail service: records system events and provides audit querying.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from sqlalchemy.orm import Session

from database import repository as repo
from database.connection import get_session
from database.schema import AuditEventTable

logger = logging.getLogger(__name__)


class AuditService:
    """Service for recording and querying audit trail events."""

    @staticmethod
    def log(
        event_type: str,
        description: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        session: Optional[Session] = None,
    ) -> None:
        """Log an audit event."""
        if session is not None:
            repo.log_audit_event(session, event_type, description, entity_type, entity_id, metadata)
        else:
            with get_session() as s:
                repo.log_audit_event(s, event_type, description, entity_type, entity_id, metadata)
        logger.info("Audit [%s]: %s (entity: %s/%s)", event_type, description, entity_type, entity_id)

    @staticmethod
    def get_recent_events(limit: int = 100, event_type: Optional[str] = None) -> list[dict]:
        """Retrieve recent audit events as dictionaries for display."""
        with get_session() as session:
            query = session.query(AuditEventTable)
            if event_type:
                query = query.filter(AuditEventTable.event_type == event_type)
            events = query.order_by(AuditEventTable.created_at.desc()).limit(limit).all()

            return [
                {
                    "id": ev.id,
                    "event_type": ev.event_type,
                    "event_description": ev.event_description,
                    "entity_type": ev.entity_type,
                    "entity_id": ev.entity_id,
                    "metadata": ev.metadata_json,
                    "created_at": ev.created_at.strftime("%Y-%m-%d %H:%M:%S") if ev.created_at else "",
                }
                for ev in events
            ]
