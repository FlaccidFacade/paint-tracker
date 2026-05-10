from __future__ import annotations

import os
from pathlib import Path

from fastapi.testclient import TestClient

TEST_DB = Path("/tmp/paint_tracker_test.db")
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"

from app.main import app  # noqa: E402
from app.models import Base  # noqa: E402
from app.database import engine  # noqa: E402


client = TestClient(app)


def setup_module() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_module() -> None:
    engine.dispose()
    if TEST_DB.exists():
        TEST_DB.unlink()


def test_create_paint_requires_room_and_coordinates_and_saves_room() -> None:
    response = client.post(
        "/api/paints",
        json={
            "room": "Living Room",
            "shelf_level": "A",
            "shelf_depth": "1",
            "color_name": "Sea Mist",
            "color_code": "SM-42",
            "finish_style": "satin",
            "bucket_image_url": "https://example.com/paint.jpg",
            "notes": "Accent wall",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["room"] == "Living Room"
    assert payload["shelf_level"] == "A"
    assert payload["shelf_depth"] == "1"

    rooms_response = client.get("/api/rooms")
    assert rooms_response.status_code == 200
    assert any(room["name"] == "Living Room" for room in rooms_response.json())


def test_room_suggestions_and_edit_mode_update() -> None:
    create_response = client.post(
        "/api/paints",
        json={
            "room": "Kitchen",
            "shelf_level": "B",
            "shelf_depth": "2",
            "color_name": "Bright White",
            "color_code": "BW-10",
            "finish_style": "matte",
            "bucket_image_url": None,
            "notes": None,
        },
    )
    paint_id = create_response.json()["id"]

    suggestions = client.get("/api/rooms", params={"suggest": "Kitch"})
    assert suggestions.status_code == 200
    assert suggestions.json()[0]["name"] == "Kitchen"

    update_response = client.put(
        f"/api/paints/{paint_id}",
        json={
            "room": "Kitchen",
            "shelf_level": "C",
            "shelf_depth": "3",
            "color_name": "Bright White",
            "color_code": "BW-10",
            "finish_style": "matte",
            "bucket_image_url": None,
            "notes": "Moved",
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["shelf_level"] == "C"
    assert update_response.json()["shelf_depth"] == "3"
