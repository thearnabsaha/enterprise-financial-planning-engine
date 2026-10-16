"""
OLAP model cache: manages instance lifecycle, lazy initialization,
and invalidation on data changes.
"""
from __future__ import annotations

import logging
import threading
from typing import Optional

from olap.adapter import OlapAdapter

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_cached_adapter: Optional[OlapAdapter] = None


def get_olap_adapter(force_refresh: bool = False) -> OlapAdapter:
    """
    Get or create the singleton OlapAdapter instance.
    If force_refresh is True or adapter is not initialized, a fresh instance is synced.
    """
    global _cached_adapter
    with _lock:
        if _cached_adapter is None or force_refresh:
            logger.info("Initializing and syncing TinyOlap cache...")
            adapter = OlapAdapter()
            try:
                adapter.sync_from_database()
            except Exception as e:
                logger.warning("Could not sync from database on init (may be unseeded yet): %s", e)
            _cached_adapter = adapter
        return _cached_adapter


def invalidate_olap_cache() -> None:
    """Invalidate cached OlapAdapter so subsequent calls trigger a re-sync."""
    global _cached_adapter
    with _lock:
        _cached_adapter = None
        logger.info("TinyOlap cache invalidated.")
