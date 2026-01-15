from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from app.core.database import get_session
from app.models.patient import Patient
from app.services.prescription_service import PrescriptionService

router = APIRouter()

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
    patient: Patient,
    session: Session = Depends(get_session)
):
    """Cria um novo paciente"""
    # Verificar se email já existe
    statement = select(Patient).where(Patient.email == patient.email)
    existing = session.exec(statement).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    session.add(patient)
    session.commit()
    session.refresh(patient)
    return patient

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
