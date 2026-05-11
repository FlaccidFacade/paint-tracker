# Re-export from canonical package for backward compatibility.
from paint_tracker.models import Base, Paint, Room

__all__ = ["Base", "Paint", "Room"]
