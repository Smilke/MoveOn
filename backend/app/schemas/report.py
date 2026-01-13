from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PeriodFilter(str, Enum):
    """Filtros de período pré-definidos"""
    LAST_WEEK = "last_week"
    LAST_MONTH = "last_month"
    LAST_3_MONTHS = "last_3_months"
    CUSTOM = "custom"


class ReportRequest(BaseModel):
    """Schema para requisição de relatório"""
    patient_id: int = Field(..., description="ID do paciente")
    period_filter: PeriodFilter = Field(
        default=PeriodFilter.LAST_MONTH,
        description="Filtro de período pré-definido"
    )
    start_date: Optional[datetime] = Field(
        None,
        description="Data de início (obrigatório se period_filter for 'custom')"
    )
    end_date: Optional[datetime] = Field(
        None,
        description="Data de fim (obrigatório se period_filter for 'custom')"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": 1,
                "period_filter": "last_month",
                "start_date": None,
                "end_date": None
            }
        }


class ExerciseLibraryBasic(BaseModel):
    """Informações básicas do exercício para relatório"""
    id: int
    name: str
    category: Optional[str] = None

    class Config:
        from_attributes = True


class PainLevelDetail(BaseModel):
    """Detalhes do nível de dor"""
    id: int
    pain_level: int
    pain_location: Optional[str] = None
    notes: Optional[str] = None
    reported_at: datetime

    class Config:
        from_attributes = True


class FeedbackDetail(BaseModel):
    """Detalhes do feedback"""
    id: int
    feedback_type: str
    content: str
    is_positive: Optional[bool] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ExerciseExecutionDetail(BaseModel):
    """Detalhes da execução de exercício"""
    id: int
    execution_date: datetime
    repetitions_completed: Optional[int] = None
    series_completed: Optional[int] = None
    duration_minutes: Optional[float] = None
    completion_rate: float
    was_completed: bool
    exercise: Optional[ExerciseLibraryBasic] = None
    pain_levels: List[PainLevelDetail] = []
    feedbacks: List[FeedbackDetail] = []

    class Config:
        from_attributes = True


class ProgressIndicator(BaseModel):
    """Indicadores de progresso"""
    total_executions: int = Field(..., description="Total de execuções no período")
    completion_rate_avg: float = Field(..., description="Taxa média de conclusão (%)")
    pain_level_avg: Optional[float] = Field(None, description="Nível médio de dor (0-10)")
    exercises_completed: int = Field(..., description="Número de exercícios completados")
    exercises_prescribed: int = Field(..., description="Número de exercícios prescritos")
    adherence_rate: float = Field(..., description="Taxa de aderência (%)")


class ReportResponse(BaseModel):
    """Schema de resposta do relatório"""
    patient_id: int
    patient_name: str
    period_start: datetime
    period_end: datetime
    generated_at: datetime
    executions: List[ExerciseExecutionDetail] = []
    progress: ProgressIndicator
    has_data: bool = Field(..., description="Indica se há dados suficientes para o relatório")

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": 1,
                "patient_name": "João Silva",
                "period_start": "2024-01-01T00:00:00",
                "period_end": "2024-01-31T23:59:59",
                "generated_at": "2024-02-01T10:00:00",
                "has_data": True,
                "executions": [],
                "progress": {
                    "total_executions": 15,
                    "completion_rate_avg": 85.5,
                    "pain_level_avg": 3.2,
                    "exercises_completed": 12,
                    "exercises_prescribed": 3,
                    "adherence_rate": 80.0
                }
            }
        }
