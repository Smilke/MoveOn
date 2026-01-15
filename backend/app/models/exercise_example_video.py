from sqlmodel import SQLModel, Field, Column, DateTime
from typing import Optional
from datetime import datetime
from sqlalchemy import func


class ExerciseExampleVideo(SQLModel, table=True):
    """Armazena o vídeo de exemplo associado a um exercício."""

    __tablename__ = "exercise_example_videos"

    id: Optional[int] = Field(default=None, primary_key=True)
    exercise_id: int = Field(foreign_key="exercise_library.id", index=True, unique=True)
    filename: str = Field(max_length=255, index=True)

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False), server_default=func.now(), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now(), nullable=False),
    )
