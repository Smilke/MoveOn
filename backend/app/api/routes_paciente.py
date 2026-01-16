from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from app.core.database import get_session
from app.models.patient import Patient
from app.models.physiotherapist import Physiotherapist

router = APIRouter()



class PacienteIn(BaseModel):
    nome: str
    cpf: str
    idade: int
    situacao: Optional[str] = "em tratamento"
    email: EmailStr
    senha: str
    fisioterapeuta_cpf: str



@router.post("/pacientes", status_code=status.HTTP_201_CREATED)
def criar_paciente(
    body: PacienteIn,
    session: Session = Depends(get_session)
):
    # Buscar fisioterapeuta pelo CPF
    fisio = session.exec(
        select(Physiotherapist).where(
            Physiotherapist.cpf == body.fisioterapeuta_cpf
        )
    ).first()

    if not fisio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fisioterapeuta com esse CPF não encontrado."
        )

    # Verificar e-mail duplicado
    paciente_existente = session.exec(
        select(Patient).where(Patient.email == body.email)
    ).first()

    if paciente_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe paciente cadastrado com esse e-mail."
        )

    # Criar paciente
    paciente = Patient(
        name=body.nome,
        email=body.email,
        phone=None,
        birth_date=None,
        physiotherapist_id=fisio.id
    )

    session.add(paciente)
    session.commit()
    session.refresh(paciente)

    return {
        "mensagem": "Paciente cadastrado com sucesso.",
        "paciente_id": paciente.id,
        "fisioterapeuta_id": fisio.id
    }



@router.get("/fisioterapeutas/{cpf}/pacientes")
def listar_pacientes_do_fisio(
    cpf: str,
    session: Session = Depends(get_session)
):
    fisio = session.exec(
        select(Physiotherapist).where(Physiotherapist.cpf == cpf)
    ).first()

    if not fisio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fisioterapeuta não encontrado."
        )

    pacientes = session.exec(
        select(Patient).where(Patient.physiotherapist_id == fisio.id)
    ).all()

    return [
        {
            "id": p.id,
            "nome": p.name,
            "email": p.email,
            "physiotherapist_id": p.physiotherapist_id
        }
        for p in pacientes
    ]