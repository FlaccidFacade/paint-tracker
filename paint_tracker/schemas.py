from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PaintBase(BaseModel):
    color_code: str | None = Field(default=None, max_length=50)
    color_name: str | None = Field(default=None, max_length=100)
    finish_style: str | None = Field(default=None, max_length=50)
    bucket_image_url: str | None = Field(default=None, max_length=500)
    notes: str | None = Field(default=None, max_length=500)
    shelf_level: str = Field(min_length=1, max_length=10)
    shelf_depth: str = Field(min_length=1, max_length=10)
    room: str = Field(min_length=1, max_length=30)


class PaintCreate(PaintBase):
    pass


class PaintUpdate(PaintBase):
    pass


class PaintOut(PaintBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class RoomOut(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)
