from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.exercise_library import DifficultyLevel

class ExerciseBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.BEGINNER)
    game_mechanics: Optional[str] = None

class ExerciseCreate(ExerciseBase):
    """Schema para criação de exercícios"""
    pass

class ExerciseUpdate(BaseModel):
    """Schema para atualização de exercícios"""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    difficulty: Optional[DifficultyLevel] = None
    game_mechanics: Optional[str] = None
    is_active: Optional[bool] = None

class ExerciseResponse(ExerciseBase):
    """Schema de resposta dos exercícios"""
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

class ExerciseSuccessResponse(BaseModel):
    """"Schema de resposta de sucesso do exercício"""
    message: str = "Exercício criado com sucesso"
    exercise: ExerciseResponse

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Exercício criado com sucesso",
                "exercise": {
                    "id": 1,
                    "name": "Agachamento",
                    "description": "Exercicio de fortalecimento de pernas",
                    "category": "Fortalecimento",
                    "difficulty": "beginner",
                    "game_mechanics": "Coletar moedas ao agachar",
                    "created_at": "2024-01-01T10:00:00",
                    "updated_at": "2024-01-01T10:00:00",
                    "is_active": True
                }
            }
        }
