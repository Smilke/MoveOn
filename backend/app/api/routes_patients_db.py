from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.database import get_session
from app.schemas.patient import PatientCreate, PatientResponse
from app.services.patient_service import PatientService

router = APIRouter()


@router.post(
    "/patients",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar paciente (banco de dados)",
    description="Cria um paciente na tabela 'patients' para ser usado em prescrições e histórico."
)
def create_patient(
    patient_data: PatientCreate,
    session: Session = Depends(get_session),
):
    try:
        patient = PatientService.create_patient(session, patient_data)
        return PatientResponse.model_validate(patient)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar paciente no banco de dados: {str(e)}",
        )


@router.get(
    "/patients",
    response_model=List[PatientResponse],
    summary="Lista pacientes cadastrados no banco",
)
def list_patients(
    session: Session = Depends(get_session),
):
    patients = PatientService.list_patients(session)
    return [PatientResponse.model_validate(p) for p in patients]


@router.get(
    "/patients/{patient_id}",
    response_model=PatientResponse,
    summary="Obtém um paciente pelo ID (banco)",
)
def get_patient(
    patient_id: int,
    session: Session = Depends(get_session),
):
    patient = PatientService.get_patient(session, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente com ID {patient_id} não encontrado.",
        )
    return PatientResponse.model_validate(patient)