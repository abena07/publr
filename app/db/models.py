import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[Optional[str]] = mapped_column(unique=True, default=None)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    instagram_user_id: Mapped[Optional[str]] = mapped_column(default=None)
    instagram_access_token: Mapped[Optional[str]] = mapped_column(default=None)
    google_access_token : Mapped[Optional[str]] = mapped_column(default=None)
    google_refresh_token : Mapped[Optional[str]] = mapped_column(default=None)
    google_token_expires_at: Mapped[Optional[int]] = mapped_column(default=None)
    gdrive_folder_id: Mapped[Optional[str]] = mapped_column(default=None)



class ProcessedFile(Base):
    __tablename__ = "processed_files"

    id : Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    gdrive_file_id: Mapped[str] = mapped_column()
    processed_at: Mapped[datetime] = mapped_column(server_default=func.now())


class FailedFile(Base):
    __tablename__ = "failed_files"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    gdrive_file_id: Mapped[str] = mapped_column()
    failed_at: Mapped[datetime] = mapped_column(server_default=func.now())
    cloudinary_url: Mapped[str] = mapped_column()