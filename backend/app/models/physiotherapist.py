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

    # Autenticação
    password_hash: Optional[str] = Field(default=None, max_length=255)
    must_change_password: bool = Field(default=False)
    password_reset_token_hash: Optional[str] = Field(default=None, max_length=64, index=True)
    password_reset_expires_at: Optional[datetime] = Field(default=None)
    
    # Relacionamentos
    patients: List["Patient"] = Relationship(back_populates="physiotherapist")
    prescriptions: List["Prescription"] = Relationship(back_populates="physiotherapist")
    goals: List["Goal"] = Relationship(back_populates="physiotherapist")
