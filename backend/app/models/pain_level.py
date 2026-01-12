from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime


class PainLevel(SQLModel, table=True):
    """Nível de dor relatado pelo paciente"""
    __tablename__ = "pain_levels"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    execution_id: int = Field(foreign_key="exercise_executions.id")
    
    # Escala de dor (0-10, onde 0 = sem dor, 10 = dor extrema)
    pain_level: int = Field(ge=0, le=10)
    pain_location: Optional[str] = Field(default=None, max_length=255)
    notes: Optional[str] = Field(default=None)
    
    reported_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Relacionamentos
    execution: "ExerciseExecution" = Relationship(back_populates="pain_levels")
