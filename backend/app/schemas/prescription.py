from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ExercisePrescriptionRequest(BaseModel):
    """Schema para requisição de prescrição de exercício"""
    patient_id: int = Field(..., description="ID do paciente")
    exercise_id: int = Field(..., description="ID do exercício da biblioteca")
    repetitions: int = Field(..., ge=1, description="Número de repetições")
    series: int = Field(..., ge=1, description="Número de séries")
    duration_minutes: Optional[int] = Field(None, ge=1, description="Duração em minutos")
    difficulty_level: Optional[str] = Field(None, max_length=50, description="Nível de dificuldade")
    weekly_frequency: int = Field(..., ge=1, description="Frequência semanal")
    notes: Optional[str] = Field(None, description="Notas adicionais")

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": 1,
                "exercise_id": 1,
                "repetitions": 10,
                "series": 3,
                "duration_minutes": 15,
                "difficulty_level": "intermediate",
                "weekly_frequency": 3,
                "notes": "Fazer com cuidado na primeira semana"
            }
        }


class PrescriptionCreate(BaseModel):
    """Schema para criação de prescrição"""
    patient_id: int
    physiotherapist_id: int
    exercise_id: int
    repetitions: int = Field(ge=1)
    series: int = Field(ge=1)
    duration_minutes: Optional[int] = Field(None, ge=1)
    difficulty_level: Optional[str] = None
    weekly_frequency: int = Field(ge=1)
    notes: Optional[str] = None


class PrescriptionUpdate(BaseModel):
    """Schema para atualização de prescrição"""
    repetitions: Optional[int] = Field(None, ge=1)
    series: Optional[int] = Field(None, ge=1)
    duration_minutes: Optional[int] = Field(None, ge=1)
    difficulty_level: Optional[str] = None
    weekly_frequency: Optional[int] = Field(None, ge=1)
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ExerciseLibraryInfo(BaseModel):
    """Informações básicas do exercício"""
    id: int
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: str
    example_video_filename: Optional[str] = None
    example_video_url: Optional[str] = None

    class Config:
        from_attributes = True


class PatientInfo(BaseModel):
    """Informações básicas do paciente"""
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


class PrescriptionResponse(BaseModel):
    """Schema de resposta da prescrição"""
    id: int
    patient_id: int
    physiotherapist_id: int
    exercise_id: int
    repetitions: int
    series: int
    duration_minutes: Optional[int] = None
    difficulty_level: Optional[str] = None
    weekly_frequency: int
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    exercise: Optional[ExerciseLibraryInfo] = None
    patient: Optional[PatientInfo] = None

    class Config:
        from_attributes = True


class PrescriptionSuccessResponse(BaseModel):
    """Schema de resposta de sucesso da prescrição"""
    message: str = "Exercício prescrito com sucesso"
    prescription: PrescriptionResponse

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Exercício prescrito com sucesso",
                "prescription": {
                    "id": 1,
                    "patient_id": 1,
                    "physiotherapist_id": 1,
                    "exercise_id": 1,
                    "repetitions": 10,
                    "series": 3,
                    "duration_minutes": 15,
                    "difficulty_level": "intermediate",
                    "weekly_frequency": 3,
                    "is_active": True,
                    "notes": "Fazer com cuidado",
                    "created_at": "2024-01-01T10:00:00",
                    "updated_at": "2024-01-01T10:00:00"
                }
            }
        }
