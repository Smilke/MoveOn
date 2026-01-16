from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select
from typing import Optional

from app.core.database import get_session
from app.core.config import settings
from app.core.security import verify_password, hash_password
from app.models.patient import Patient
from app.models.physiotherapist import Physiotherapist

router = APIRouter()


class LoginIn(BaseModel):
    email: EmailStr
    senha: str


class LoginOut(BaseModel):
    tipo: str
    id: int
    nome: str
    email: EmailStr
    cpf: Optional[str] = None
    must_change_password: bool = False


@router.post("/login", response_model=LoginOut)
def login(body: LoginIn, session: Session = Depends(get_session)):
    # Tenta fisioterapeuta
    fisio = session.exec(
        select(Physiotherapist).where(Physiotherapist.email == body.email)
    ).first()

    if fisio:
        if not fisio.password_hash:
            fisio.password_hash = hash_password(settings.DEFAULT_PHYSIO_PASSWORD)
            session.add(fisio)
            session.commit()
            session.refresh(fisio)

        if not verify_password(body.senha, fisio.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha inválidos.",
            )
        return LoginOut(
            tipo="fisioterapeuta",
            id=fisio.id,
            nome=getattr(fisio, "name", "") or "",
            email=fisio.email,
            cpf=getattr(fisio, "cpf", None),
            must_change_password=bool(getattr(fisio, "must_change_password", False)),
        )

    # Tenta paciente
    paciente = session.exec(
        select(Patient).where(Patient.email == body.email)
    ).first()

    if paciente:
        if not paciente.password_hash:
            paciente.password_hash = hash_password(settings.DEFAULT_PATIENT_PASSWORD)
            paciente.must_change_password = True
            session.add(paciente)
            session.commit()
            session.refresh(paciente)

        if not verify_password(body.senha, paciente.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha inválidos.",
            )
        return LoginOut(
            tipo="paciente",
            id=paciente.id,
            nome=getattr(paciente, "name", "") or "",
            email=paciente.email,
            cpf=getattr(paciente, "cpf", None),
            must_change_password=bool(getattr(paciente, "must_change_password", False)),
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Email ou senha inválidos.",
    )