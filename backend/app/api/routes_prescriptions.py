from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from typing import List

from app.core.database import get_session
from app.services.prescription_service import PrescriptionService
from app.schemas.prescription import (
    ExercisePrescriptionRequest,
    PrescriptionResponse,
    PrescriptionSuccessResponse,
)
from app.models.exercise_library import ExerciseLibrary
from app.models.prescription import Prescription

router = APIRouter()


@router.post(
    "/prescriptions",
    response_model=PrescriptionSuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Prescreve um exercício gamificado para um paciente",
    description="Permite ao fisioterapeuta prescrever um exercício da biblioteca para um paciente, configurando parâmetros como repetições, séries, duração, dificuldade e frequência semanal. O physiotherapist_id deve ser fornecido como query parameter (em produção, viria do token de autenticação)"
)
def create_prescription(
    prescription_data: ExercisePrescriptionRequest,
    physiotherapist_id: int = Query(..., description="ID do fisioterapeuta (em produção viria do token)"),
    session: Session = Depends(get_session)
):
    """
    Cria uma nova prescrição de exercício para um paciente.
    
    O exercício prescrito aparecerá na lista de exercícios do paciente.
    """
    try:
        from app.schemas.prescription import PrescriptionCreate
        
        prescription_create = PrescriptionCreate(
            patient_id=prescription_data.patient_id,
            physiotherapist_id=physiotherapist_id,
            exercise_id=prescription_data.exercise_id,
            repetitions=prescription_data.repetitions,
            series=prescription_data.series,
            duration_minutes=prescription_data.duration_minutes,
            difficulty_level=prescription_data.difficulty_level,
            weekly_frequency=prescription_data.weekly_frequency,
            notes=prescription_data.notes,
        )
        
        prescription = PrescriptionService.create_prescription(session, prescription_create)
        
        # Buscar dados relacionados para a resposta
        from app.models.patient import Patient
        exercise = session.get(ExerciseLibrary, prescription.exercise_id)
        patient = session.get(Patient, prescription.patient_id)
        
        prescription_response = PrescriptionResponse(
            id=prescription.id,
            patient_id=prescription.patient_id,
            physiotherapist_id=prescription.physiotherapist_id,
            exercise_id=prescription.exercise_id,
            repetitions=prescription.repetitions,
            series=prescription.series,
            duration_minutes=prescription.duration_minutes,
            difficulty_level=prescription.difficulty_level,
            weekly_frequency=prescription.weekly_frequency,
            is_active=prescription.is_active,
            notes=prescription.notes,
            created_at=prescription.created_at,
            updated_at=prescription.updated_at,
            exercise=exercise,
            patient=patient,
        )
        
        return PrescriptionSuccessResponse(
            message="Exercício prescrito com sucesso",
            prescription=prescription_response
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/patients/{patient_id}/prescriptions",
    response_model=List[PrescriptionResponse],
    summary="Lista todas as prescrições de um paciente",
    description="Retorna a lista completa de exercícios prescritos para um paciente específico"
)
def get_patient_prescriptions(
    patient_id: int,
    active_only: bool = True,
    session: Session = Depends(get_session)
):
    """Lista todas as prescrições de um paciente"""
    prescriptions = PrescriptionService.get_patient_prescriptions(
        session, patient_id, active_only=active_only
    )
    
    # Enriquecer com dados relacionados
    from app.models.patient import Patient
    result = []
    for prescription in prescriptions:
        exercise = session.get(ExerciseLibrary, prescription.exercise_id)
        patient = session.get(Patient, prescription.patient_id)
        
        prescription_response = PrescriptionResponse(
            id=prescription.id,
            patient_id=prescription.patient_id,
            physiotherapist_id=prescription.physiotherapist_id,
            exercise_id=prescription.exercise_id,
            repetitions=prescription.repetitions,
            series=prescription.series,
            duration_minutes=prescription.duration_minutes,
            difficulty_level=prescription.difficulty_level,
            weekly_frequency=prescription.weekly_frequency,
            is_active=prescription.is_active,
            notes=prescription.notes,
            created_at=prescription.created_at,
            updated_at=prescription.updated_at,
            exercise=exercise,
            patient=patient,
        )
        result.append(prescription_response)
    
    return result


@router.get(
    "/prescriptions/{prescription_id}",
    response_model=PrescriptionResponse,
    summary="Obtém detalhes de uma prescrição específica",
    description="Retorna os detalhes completos de uma prescrição de exercício"
)
def get_prescription(
    prescription_id: int,
    session: Session = Depends(get_session)
):
    """Obtém uma prescrição específica"""
    prescription = PrescriptionService.get_prescription(session, prescription_id)
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prescrição com ID {prescription_id} não encontrada"
        )
    
    from app.models.patient import Patient
    exercise = session.get(ExerciseLibrary, prescription.exercise_id)
    patient = session.get(Patient, prescription.patient_id)
    
    return PrescriptionResponse(
        id=prescription.id,
        patient_id=prescription.patient_id,
        physiotherapist_id=prescription.physiotherapist_id,
        exercise_id=prescription.exercise_id,
        repetitions=prescription.repetitions,
        series=prescription.series,
        duration_minutes=prescription.duration_minutes,
        difficulty_level=prescription.difficulty_level,
        weekly_frequency=prescription.weekly_frequency,
        is_active=prescription.is_active,
        notes=prescription.notes,
        created_at=prescription.created_at,
        updated_at=prescription.updated_at,
        exercise=exercise,
        patient=patient,
    )
