from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select
from typing import Optional

from app.core.database import get_session
from app.models.patient import Patient
from app.models.physiotherapist import Physiotherapist

router = APIRouter()

SENHA_PADRAO = "Senha124"


class LoginIn(BaseModel):
    email: EmailStr
    senha: str


class LoginOut(BaseModel):
    tipo: str
    id: int
    nome: str
    email: EmailStr
    cpf: Optional[str] = None


@router.post("/login", response_model=LoginOut)
def login(body: LoginIn, session: Session = Depends(get_session)):
    # senha padrão (pra destravar o fluxo)
    if body.senha != SENHA_PADRAO:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos.",
        )

    # 1) tenta fisio
    fisio = session.exec(
        select(Physiotherapist).where(Physiotherapist.email == body.email)
    ).first()

    if fisio:
        return LoginOut(
            tipo="fisioterapeuta",
            id=fisio.id,
            nome=getattr(fisio, "name", "") or "",
            email=fisio.email,
            cpf=getattr(fisio, "cpf", None),
        )

    # 2) tenta paciente
    paciente = session.exec(
        select(Patient).where(Patient.email == body.email)
    ).first()

    if paciente:
        return LoginOut(
            tipo="paciente",
            id=paciente.id,
            nome=getattr(paciente, "name", "") or "",
            email=paciente.email,
            cpf=getattr(paciente, "cpf", None),
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Email ou senha inválidos.",
    )