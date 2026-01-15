from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, constr


class PhysiotherapistBase(BaseModel):
    """Campos base para fisioterapeuta (lado da API)."""
    name: str = Field(..., max_length=255)
    cpf: constr(min_length=11, max_length=11)  # só dígitos
    email: EmailStr
    license_number: str = Field(..., max_length=50)


class PhysiotherapistCreate(PhysiotherapistBase):
    """Payload de criação de fisioterapeuta."""
    # por enquanto sem senha no banco pra não quebrar o schema já criado
    pass


class PhysiotherapistResponse(PhysiotherapistBase):
    """Retorno padrão de fisioterapeuta pela API."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # pydantic v2 + SQLModel