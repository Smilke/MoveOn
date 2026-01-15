from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timedelta

class PasswordResetToken(SQLModel, table=True):
    """
    Tabela para armazenar tokens de recuperação de senha.
    """
    __tablename__ = "password_reset_tokens"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_email: str = Field(index=True)
    user_type: str = Field(description="fisio ou paciente")
    token: str = Field(unique=True, index=True)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(hours=1))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_used: bool = Field(default=False)
