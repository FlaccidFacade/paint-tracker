# Re-export everything from the canonical package so that
# `backend/tests/` and legacy imports continue to work unchanged.
from paint_tracker.database import (  # noqa: F401
    DATABASE_URL,
    session_local,
    engine,
    get_db,
)
