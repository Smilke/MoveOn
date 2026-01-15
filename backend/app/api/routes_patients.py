from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from app.core.database import get_session
from app.models.patient import Patient

router = APIRouter()

class PatientCreate(BaseModel):
    name: str
    email: str
    cpf: str
    physiotherapist_id: Optional[int] = None

@router.get(
    "/patients",
    response_model=List[Patient],
    summary="Lista todos os pacientes",
    description="Retorna a lista de todos os pacientes cadastrados"
)
def list_patients(
    session: Session = Depends(get_session)
):
    """Lista todos os pacientes"""
    statement = select(Patient).order_by(Patient.name)
    patients = session.exec(statement).all()
    return patients

@router.post(
    "/patients",
    response_model=Patient,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastra um novo paciente",
    description="Cria um novo paciente no sistema"
)
def create_patient(
    body: PatientCreate,
    session: Session = Depends(get_session)
):
    """Cria um novo paciente"""
    # Verificar se email já existe
    statement = select(Patient).where(Patient.email == body.email)
    existing = session.exec(statement).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Verificar se CPF já existe
    stmt_cpf = select(Patient).where(Patient.cpf == body.cpf)
    existing_cpf = session.exec(stmt_cpf).first()
    if existing_cpf:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF já cadastrado"
        )
    
    nuevo_paciente = Patient(
        name=body.name,
        email=body.email,
        cpf=body.cpf,
        physiotherapist_id=body.physiotherapist_id
    )
    
    session.add(nuevo_paciente)
    session.commit()
    session.refresh(nuevo_paciente)
    return nuevo_paciente

@router.get(
    "/patients/{patient_id}",
    response_model=Patient,
    summary="Obtém detalhes de um paciente",
    description="Retorna os dados cadastrais de um paciente específico"
)
def get_patient(
    patient_id: int,
    session: Session = Depends(get_session)
):
    """Obtém detalhes de um paciente"""
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente {patient_id} não encontrado"
        )
    return patient
