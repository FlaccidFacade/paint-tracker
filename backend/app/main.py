# Re-export the canonical FastAPI app for backward compatibility
# (e.g. ``uvicorn app.main:app`` from the backend directory still works).
from paint_tracker.main import app

__all__ = ["app"]
