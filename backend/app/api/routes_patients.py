from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from app.core.database import get_session
from app.models.patient import Patient
from app.models.goal import Goal
from app.models.prescription import Prescription
from app.models.exercise_execution import ExerciseExecution
from app.models.pain_level import PainLevel
from app.models.feedback import Feedback

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


@router.get(
    "/physiotherapists/{physio_id}/patients",
    response_model=List[Patient],
    summary="Lista pacientes de um fisioterapeuta",
    description="Retorna apenas os pacientes vinculados (patients.physiotherapist_id) ao fisioterapeuta informado"
)
def list_patients_for_physiotherapist(
    physio_id: int,
    session: Session = Depends(get_session),
):
    statement = (
        select(Patient)
        .where(Patient.physiotherapist_id == physio_id)
        .order_by(Patient.name)
    )
    return session.exec(statement).all()

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


@router.delete(
    "/physiotherapists/{physio_id}/patients/{patient_id}",
    status_code=status.HTTP_200_OK,
    summary="Remove um paciente (fisioterapeuta)",
    description="Hard delete do paciente. Remove também prescrições, execuções (e dor/feedbacks) e metas vinculadas para não quebrar FKs.",
)
def delete_patient_for_physiotherapist(
    physio_id: int,
    patient_id: int,
    session: Session = Depends(get_session),
):
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente {patient_id} não encontrado",
        )
    if patient.physiotherapist_id != physio_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: paciente não vinculado a este fisioterapeuta",
        )

    try:
        # 1) Metas
        goals = list(session.exec(select(Goal).where(Goal.patient_id == patient_id)).all())
        for g in goals:
            session.delete(g)

        # 2) Execuções + dependentes (dor/feedbacks)
        executions = list(
            session.exec(select(ExerciseExecution).where(ExerciseExecution.patient_id == patient_id)).all()
        )
        for ex in executions:
            pains = list(session.exec(select(PainLevel).where(PainLevel.execution_id == ex.id)).all())
            for p in pains:
                session.delete(p)

            fbs = list(session.exec(select(Feedback).where(Feedback.execution_id == ex.id)).all())
            for f in fbs:
                session.delete(f)

            session.delete(ex)

        # 3) Prescrições (após remover execuções)
        prescriptions = list(
            session.exec(select(Prescription).where(Prescription.patient_id == patient_id)).all()
        )
        for pr in prescriptions:
            session.delete(pr)

        # 4) Paciente
        session.delete(patient)
        session.commit()
        return {"message": "Paciente removido permanentemente"}
    except Exception as e:  # noqa: BLE001
        if session.in_transaction():
            session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover paciente: {str(e)}",
        )
