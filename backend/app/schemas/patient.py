from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class PatientBase(BaseModel):
    """Campos base para paciente (lado da API)"""
    name: str = Field(..., max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=20)
    birth_date: Optional[datetime] = None
    physiotherapist_id: Optional[int] = Field(
        default=None,
        description="ID do fisioterapeuta responsável (tabela physiotherapists)"
    )


class PatientCreate(PatientBase):
    """Payload de criação de paciente"""
    pass


class PatientResponse(PatientBase):
    """Paciente retornado pela API (inclui ID e datas)"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # pydantic v2 + SQLModel