from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    paints: Mapped[list["Paint"]] = relationship(back_populates="room", cascade="all, delete-orphan")


class Paint(Base):
    __tablename__ = "paints"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    color_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    color_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    finish_style: Mapped[str | None] = mapped_column(String(50), nullable=True)
    bucket_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    shelf_level: Mapped[str] = mapped_column(String(10), index=True)
    shelf_depth: Mapped[str] = mapped_column(String(10), index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), index=True)
    room: Mapped[Room] = relationship(back_populates="paints")
