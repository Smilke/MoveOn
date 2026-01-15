from __future__ import annotations
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.patient import Patient
    from app.models.physiotherapist import Physiotherapist

class Goal(SQLModel, table=True):
    """Modelo de Meta para o paciente"""
    __tablename__ = "goals"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patients.id")
    physiotherapist_id: int = Field(foreign_key="physiotherapists.id")
    
    description: str = Field(max_length=500)
    success_criteria: Optional[str] = Field(default=None, max_length=500)
    
    # Status permitidos: 'ativa', 'em_andamento', 'concluida', 'nao_atingida'
    status: str = Field(default="ativa", max_length=50)
    
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = Field(default=None)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
    
    # Relacionamentos
    patient: Patient = Relationship(back_populates="goals")
    physiotherapist: Physiotherapist = Relationship(back_populates="goals")
