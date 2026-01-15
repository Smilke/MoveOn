from sqlmodel import SQLModel, Field, Column, DateTime
from typing import Optional
from datetime import datetime
from enum import Enum
from sqlalchemy import func


class DifficultyLevel(str, Enum):
    """Níveis de dificuldade dos exercícios"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ExerciseLibrary(SQLModel, table=True):
    """Biblioteca de exercícios gamificados disponíveis"""
    __tablename__ = "exercise_library"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, index=True)
    description: Optional[str] = Field(default=None)
    category: Optional[str] = Field(default=None, max_length=100)
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.BEGINNER)
    game_mechanics: Optional[str] = Field(default=None)  # Descrição da mecânica gamificada
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False), server_default=func.now(), nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now(), nullable=False)
    )
    is_active: bool = Field(default=True)
