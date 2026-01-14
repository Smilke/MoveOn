from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime


class ExerciseExecution(SQLModel, table=True):
    """Execução de exercício pelo paciente"""
    __tablename__ = "exercise_executions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    prescription_id: int = Field(foreign_key="prescriptions.id")
    patient_id: int = Field(foreign_key="patients.id")
    
    # Dados da execução
    execution_date: datetime = Field(default_factory=datetime.utcnow, index=True)
    repetitions_completed: Optional[int] = Field(default=None, ge=0)
    series_completed: Optional[int] = Field(default=None, ge=0)
    duration_minutes: Optional[float] = Field(default=None, ge=0)
    completion_rate: float = Field(default=0.0, ge=0.0, le=100.0)  # Taxa de conclusão em %
    was_completed: bool = Field(default=False)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relacionamentos
    prescription: "Prescription" = Relationship(back_populates="executions")
    patient: "Patient" = Relationship(back_populates="exercise_executions")
    pain_levels: list["PainLevel"] = Relationship(back_populates="execution")
    feedbacks: list["Feedback"] = Relationship(back_populates="execution")
