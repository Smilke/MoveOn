from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PeriodFilter(str, Enum):
    """Filtros de período pré-definidos"""
    LAST_7_DAYS = "last_7_days"
    LAST_MONTH = "last_month"
    LAST_3_MONTHS = "last_3_months"
    CUSTOM = "custom"


class PainEvolutionItem(BaseModel):
    """Item da evolução da dor"""
    date: datetime
    pain_level: float = Field(..., ge=0.0, le=10.0, description="Nível médio de dor no dia")
    execution_count: int = Field(..., description="Número de execuções no dia")

    class Config:
        from_attributes = True


class ExerciseProgress(BaseModel):
    """Progresso por exercício"""
    exercise_id: int
    exercise_name: str
    total_executions: int
    completion_rate_avg: float = Field(..., ge=0.0, le=100.0)
    days_performed: int = Field(..., description="Dias em que o exercício foi realizado")
    last_execution_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class GoalAchievement(BaseModel):
    """Meta alcançada"""
    goal_type: str = Field(..., description="Tipo de meta (ex: 'exercises_per_week')")
    target: float = Field(..., description="Valor da meta")
    achieved: float = Field(..., description="Valor alcançado")
    percentage: float = Field(..., ge=0.0, le=100.0, description="Percentual alcançado")
    is_achieved: bool = Field(..., description="Se a meta foi alcançada")


class ProgressReportResponse(BaseModel):
    """Resposta do relatório de progresso"""
    patient_id: int
    patient_name: str
    period_start: datetime
    period_end: datetime
    generated_at: datetime
    
    # Resumo geral
    total_days_with_exercise: int = Field(..., description="Dias em que fez exercício")
    total_activity_time_minutes: float = Field(..., ge=0.0, description="Tempo total de atividade (minutos)")
    total_executions: int = Field(..., description="Total de execuções no período")
    average_completion_rate: float = Field(..., ge=0.0, le=100.0, description="Taxa média de conclusão (%)")
    
    # Evolução da dor
    pain_evolution: List[PainEvolutionItem] = Field(default_factory=list, description="Evolução da dor ao longo do período")
    average_pain_level: Optional[float] = Field(None, ge=0.0, le=10.0, description="Nível médio de dor no período")
    
    # Progresso por exercício
    exercises_progress: List[ExerciseProgress] = Field(default_factory=list)
    
    # Metas
    goals_achieved: List[GoalAchievement] = Field(default_factory=list)
    
    # Status
    has_data: bool = Field(..., description="Indica se há dados suficientes para o relatório")
    message: Optional[str] = Field(None, description="Mensagem quando não há dados suficientes")

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": 1,
                "patient_name": "João Silva",
                "period_start": "2024-01-01T00:00:00",
                "period_end": "2024-01-31T23:59:59",
                "generated_at": "2024-02-01T10:00:00",
                "total_days_with_exercise": 20,
                "total_activity_time_minutes": 300.0,
                "total_executions": 25,
                "average_completion_rate": 85.5,
                "average_pain_level": 3.2,
                "has_data": True,
                "pain_evolution": [],
                "exercises_progress": [],
                "goals_achieved": []
            }
        }
