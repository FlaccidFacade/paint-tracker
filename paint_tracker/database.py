"""Database engine / session factory with automatic data-directory creation."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def _default_db_path() -> str:
    """Return a sensible default SQLite path inside the user's data directory.

    Priority:
    1. ``DATABASE_URL`` environment variable (any SQLAlchemy URL).
    2. ``~/.local/share/paint-tracker/paint_tracker.db``  (XDG-ish default).
    """
    data_dir = Path.home() / ".local" / "share" / "paint-tracker"
    data_dir.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{data_dir / 'paint_tracker.db'}"


DATABASE_URL: str = os.getenv("DATABASE_URL") or _default_db_path()

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
