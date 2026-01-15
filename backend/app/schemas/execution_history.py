from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ExecutionStatus(str, Enum):
    """Status da execução do exercício"""
    COMPLETED = "concluído"
    PARTIAL = "parcial"
    NOT_COMPLETED = "não concluído"


class PeriodFilter(str, Enum):
    """Filtros de período pré-definidos para histórico"""
    LAST_7_DAYS = "last_7_days"
    LAST_MONTH = "last_month"
    CUSTOM = "custom"


class ExecutionCreate(BaseModel):
    """Dados para registrar uma execução de exercício"""
    prescription_id: int
    repetitions_completed: int
    series_completed: int
    duration_minutes: Optional[int] = None
    was_completed: bool = True
    pain_level: Optional[int] = Field(None, ge=0, le=10)
    feedback_comment: Optional[str] = None



class ExerciseBasicInfo(BaseModel):
    """Informações básicas do exercício"""
    id: int
    name: str
    category: Optional[str] = None

    class Config:
        from_attributes = True


class PainLevelInfo(BaseModel):
    """Informações do nível de dor"""
    pain_level: int = Field(..., ge=0, le=10, description="Nível de dor (0-10)")
    pain_location: Optional[str] = None
    reported_at: datetime

    class Config:
        from_attributes = True


class ExecutionHistoryItem(BaseModel):
    """Item do histórico de execução"""
    id: int
    execution_date: datetime
    exercise: ExerciseBasicInfo
    status: ExecutionStatus = Field(..., description="Status da execução")
    completion_rate: float = Field(..., ge=0.0, le=100.0, description="Taxa de conclusão (%)")
    repetitions_completed: Optional[int] = None
    series_completed: Optional[int] = None
    duration_minutes: Optional[float] = None
    pain_level: Optional[PainLevelInfo] = Field(None, description="Nível de dor se disponível")

    class Config:
        from_attributes = True


class ExecutionHistoryResponse(BaseModel):
    """Resposta do histórico de execução"""
    patient_id: int
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    total_executions: int = Field(..., description="Total de execuções no período")
    executions: List[ExecutionHistoryItem] = []
    has_data: bool = Field(..., description="Indica se há histórico de execuções")
    message: Optional[str] = Field(None, description="Mensagem quando não há histórico")

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": 1,
                "period_start": "2024-01-01T00:00:00",
                "period_end": "2024-01-31T23:59:59",
                "total_executions": 5,
                "has_data": True,
                "executions": [
                    {
                        "id": 1,
                        "execution_date": "2024-01-15T10:00:00",
                        "exercise": {
                            "id": 1,
                            "name": "Agachamento",
                            "category": "Fortalecimento"
                        },
                        "status": "concluído",
                        "completion_rate": 100.0,
                        "repetitions_completed": 10,
                        "series_completed": 3,
                        "duration_minutes": 15.0,
                        "pain_level": {
                            "pain_level": 2,
                            "pain_location": "Perna direita",
                            "reported_at": "2024-01-15T10:15:00"
                        }
                    }
                ]
            }
        }
