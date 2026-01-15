from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime


class Patient(SQLModel, table=True):
    """Modelo de Paciente"""
    __tablename__ = "patients"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    cpf: str = Field(max_length=11, unique=True, index=True)
    email: str = Field(max_length=255, unique=True, index=True)
    phone: Optional[str] = Field(default=None, max_length=20)
    birth_date: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
    
    # Relacionamentos
    physiotherapist_id: Optional[int] = Field(default=None, foreign_key="physiotherapists.id")
    physiotherapist: Optional["Physiotherapist"] = Relationship(back_populates="patients")
    prescriptions: List["Prescription"] = Relationship(back_populates="patient")
    exercise_executions: List["ExerciseExecution"] = Relationship(back_populates="patient")
    goals: List["Goal"] = Relationship(back_populates="patient")
