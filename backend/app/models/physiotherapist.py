from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime


class Physiotherapist(SQLModel, table=True):
    """Modelo de Fisioterapeuta"""
    __tablename__ = "physiotherapists"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    cpf : str = Field(max_length=11, unique=True, index=True)
    email: str = Field(max_length=255, unique=True, index=True)
    license_number: str = Field(max_length=50, unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
    
    # Relacionamentos
    patients: List["Patient"] = Relationship(back_populates="physiotherapist")
    prescriptions: List["Prescription"] = Relationship(back_populates="physiotherapist")
