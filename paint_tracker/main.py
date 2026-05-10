from __future__ import annotations

from difflib import get_close_matches
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import engine, get_db
from .models import Base, Paint, Room
from .schemas import PaintCreate, PaintOut, PaintUpdate, RoomOut

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Paint Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _normalize_room_name(room_name: str) -> str:
    return room_name.strip()


def _get_or_create_room(db: Session, room_name: str) -> Room:
    normalized_name = _normalize_room_name(room_name)
    existing = db.execute(select(Room).where(Room.name.ilike(normalized_name))).scalar_one_or_none()
    if existing:
        return existing

    room = Room(name=normalized_name)
    db.add(room)
    db.flush()
    return room


def _paint_to_schema(paint: Paint) -> PaintOut:
    return PaintOut(
        id=paint.id,
        color_code=paint.color_code,
        color_name=paint.color_name,
        finish_style=paint.finish_style,
        bucket_image_url=paint.bucket_image_url,
        notes=paint.notes,
        shelf_level=paint.shelf_level,
        shelf_depth=paint.shelf_depth,
        room=paint.room.name,
    )


@app.get("/api/paints", response_model=list[PaintOut])
def list_paints(
    query: str | None = Query(default=None, max_length=100),
    db: Session = Depends(get_db),
) -> list[PaintOut]:
    statement = select(Paint).join(Room)
    if query:
        q = f"%{query.strip()}%"
        statement = statement.where(
            Paint.color_name.ilike(q)
            | Paint.color_code.ilike(q)
            | Room.name.ilike(q)
            | Paint.shelf_level.ilike(q)
            | Paint.shelf_depth.ilike(q)
        )

    paints = db.execute(statement.order_by(Room.name, Paint.shelf_level, Paint.shelf_depth)).scalars().all()
    return [_paint_to_schema(paint) for paint in paints]


@app.post("/api/paints", response_model=PaintOut, status_code=201)
def create_paint(payload: PaintCreate, db: Session = Depends(get_db)) -> PaintOut:
    room = _get_or_create_room(db, payload.room)
    paint = Paint(
        color_code=payload.color_code,
        color_name=payload.color_name,
        finish_style=payload.finish_style,
        bucket_image_url=payload.bucket_image_url,
        notes=payload.notes,
        shelf_level=payload.shelf_level,
        shelf_depth=payload.shelf_depth,
        room_id=room.id,
    )
    db.add(paint)
    db.commit()
    db.refresh(paint)
    db.refresh(paint, attribute_names=["room"])
    return _paint_to_schema(paint)


@app.put("/api/paints/{paint_id}", response_model=PaintOut)
def update_paint(paint_id: int, payload: PaintUpdate, db: Session = Depends(get_db)) -> PaintOut:
    paint = db.get(Paint, paint_id)
    if not paint:
        raise HTTPException(status_code=404, detail="Paint not found")

    room = _get_or_create_room(db, payload.room)
    paint.color_code = payload.color_code
    paint.color_name = payload.color_name
    paint.finish_style = payload.finish_style
    paint.bucket_image_url = payload.bucket_image_url
    paint.notes = payload.notes
    paint.shelf_level = payload.shelf_level
    paint.shelf_depth = payload.shelf_depth
    paint.room_id = room.id

    db.commit()
    db.refresh(paint)
    db.refresh(paint, attribute_names=["room"])
    return _paint_to_schema(paint)


@app.get("/api/rooms", response_model=list[RoomOut])
def list_rooms(
    suggest: str | None = Query(default=None, max_length=30),
    db: Session = Depends(get_db),
) -> list[RoomOut]:
    rooms = db.execute(select(Room).order_by(Room.name)).scalars().all()
    if not suggest:
        return rooms

    room_names = [room.name for room in rooms]
    suggestion = suggest.strip()
    prefix_matches = [name for name in room_names if suggestion.lower() in name.lower()]
    close_matches = get_close_matches(suggestion, room_names, n=5, cutoff=0.5)
    ordered_names = list(dict.fromkeys(prefix_matches + close_matches))

    return [room for room in rooms if room.name in ordered_names]


# Serve the pre-built React frontend when it exists inside the package.
# This mount must be registered AFTER all API routes so that API paths take
# priority over the catch-all "/" prefix handled by StaticFiles.
_STATIC_DIR = Path(__file__).parent / "static"
if (_STATIC_DIR / "index.html").exists():
    app.mount("/", StaticFiles(directory=str(_STATIC_DIR), html=True), name="static")


def _normalize_room_name(room_name: str) -> str:
    return room_name.strip()


def _get_or_create_room(db: Session, room_name: str) -> Room:
    normalized_name = _normalize_room_name(room_name)
    existing = db.execute(select(Room).where(Room.name.ilike(normalized_name))).scalar_one_or_none()
    if existing:
        return existing

    room = Room(name=normalized_name)
    db.add(room)
    db.flush()
    return room


def _paint_to_schema(paint: Paint) -> PaintOut:
    return PaintOut(
        id=paint.id,
        color_code=paint.color_code,
        color_name=paint.color_name,
        finish_style=paint.finish_style,
        bucket_image_url=paint.bucket_image_url,
        notes=paint.notes,
        shelf_level=paint.shelf_level,
        shelf_depth=paint.shelf_depth,
        room=paint.room.name,
    )


@app.get("/api/paints", response_model=list[PaintOut])
def list_paints(
    query: str | None = Query(default=None, max_length=100),
    db: Session = Depends(get_db),
) -> list[PaintOut]:
    statement = select(Paint).join(Room)
    if query:
        q = f"%{query.strip()}%"
        statement = statement.where(
            Paint.color_name.ilike(q)
            | Paint.color_code.ilike(q)
            | Room.name.ilike(q)
            | Paint.shelf_level.ilike(q)
            | Paint.shelf_depth.ilike(q)
        )

    paints = db.execute(statement.order_by(Room.name, Paint.shelf_level, Paint.shelf_depth)).scalars().all()
    return [_paint_to_schema(paint) for paint in paints]


@app.post("/api/paints", response_model=PaintOut, status_code=201)
def create_paint(payload: PaintCreate, db: Session = Depends(get_db)) -> PaintOut:
    room = _get_or_create_room(db, payload.room)
    paint = Paint(
        color_code=payload.color_code,
        color_name=payload.color_name,
        finish_style=payload.finish_style,
        bucket_image_url=payload.bucket_image_url,
        notes=payload.notes,
        shelf_level=payload.shelf_level,
        shelf_depth=payload.shelf_depth,
        room_id=room.id,
    )
    db.add(paint)
    db.commit()
    db.refresh(paint)
    db.refresh(paint, attribute_names=["room"])
    return _paint_to_schema(paint)


@app.put("/api/paints/{paint_id}", response_model=PaintOut)
def update_paint(paint_id: int, payload: PaintUpdate, db: Session = Depends(get_db)) -> PaintOut:
    paint = db.get(Paint, paint_id)
    if not paint:
        raise HTTPException(status_code=404, detail="Paint not found")

    room = _get_or_create_room(db, payload.room)
    paint.color_code = payload.color_code
    paint.color_name = payload.color_name
    paint.finish_style = payload.finish_style
    paint.bucket_image_url = payload.bucket_image_url
    paint.notes = payload.notes
    paint.shelf_level = payload.shelf_level
    paint.shelf_depth = payload.shelf_depth
    paint.room_id = room.id

    db.commit()
    db.refresh(paint)
    db.refresh(paint, attribute_names=["room"])
    return _paint_to_schema(paint)


@app.get("/api/rooms", response_model=list[RoomOut])
def list_rooms(
    suggest: str | None = Query(default=None, max_length=30),
    db: Session = Depends(get_db),
) -> list[RoomOut]:
    rooms = db.execute(select(Room).order_by(Room.name)).scalars().all()
    if not suggest:
        return rooms

    room_names = [room.name for room in rooms]
    suggestion = suggest.strip()
    prefix_matches = [name for name in room_names if suggestion.lower() in name.lower()]
    close_matches = get_close_matches(suggestion, room_names, n=5, cutoff=0.5)
    ordered_names = list(dict.fromkeys(prefix_matches + close_matches))

    return [room for room in rooms if room.name in ordered_names]
