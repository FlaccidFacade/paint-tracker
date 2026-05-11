# Re-export from canonical package for backward compatibility.
from paint_tracker.schemas import (
    PaintBase,
    PaintCreate,
    PaintOut,
    PaintUpdate,
    RoomOut,
)

__all__ = ["PaintBase", "PaintCreate", "PaintOut", "PaintUpdate", "RoomOut"]
