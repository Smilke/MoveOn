from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime


class Prescription(SQLModel, table=True):
    """Prescrição de exercício para um paciente"""
    __tablename__ = "prescriptions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patients.id")
    physiotherapist_id: int = Field(foreign_key="physiotherapists.id")
    exercise_id: int = Field(foreign_key="exercise_library.id")
    
    # Parâmetros do exercício
    repetitions: int = Field(default=1, ge=1)
    series: int = Field(default=1, ge=1)
    duration_minutes: Optional[int] = Field(default=None, ge=1)  # Duração em minutos
    difficulty_level: Optional[str] = Field(default=None, max_length=50)
    weekly_frequency: int = Field(default=1, ge=1)  # Frequência semanal
    
    # Status
    is_active: bool = Field(default=True)
    notes: Optional[str] = Field(default=None)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
    
    # Relacionamentos
    patient: "Patient" = Relationship(back_populates="prescriptions")
    physiotherapist: "Physiotherapist" = Relationship(back_populates="prescriptions")
    exercise: "ExerciseLibrary" = Relationship()
    executions: list["ExerciseExecution"] = Relationship(back_populates="prescription")
