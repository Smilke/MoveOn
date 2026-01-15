from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class ExerciseExecution(SQLModel, table=True):
    __tablename__ = "exercise_executions"

    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patients.id")
    prescription_id: int = Field(foreign_key="prescriptions.id")
    
    execution_date: datetime = Field(default_factory=datetime.utcnow)
    repetitions_completed: int
    series_completed: int
    duration_minutes: Optional[int] = None
    
    completion_rate: float = 0.0
    was_completed: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relacionamentos
    patient: "Patient" = Relationship(back_populates="exercise_executions")
    prescription: "Prescription" = Relationship(back_populates="executions")
    pain_levels: List["PainLevel"] = Relationship(back_populates="execution")
