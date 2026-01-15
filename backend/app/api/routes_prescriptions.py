from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from typing import List

from app.core.database import get_session
from app.services.prescription_service import PrescriptionService
from app.schemas.prescription import (
    ExercisePrescriptionRequest,
    PrescriptionResponse,
    PrescriptionSuccessResponse,
    PrescriptionUpdateRequest,
    PrescriptionUpdate,
    PrescriptionHistoryResponse,
    PhysiotherapistInfo,
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


@router.put(
    "/prescriptions/{prescription_id}",
    response_model=PrescriptionResponse,
    summary="Atualiza os parâmetros de uma prescrição",
    description="Permite ao fisioterapeuta atualizar métricas do exercício prescrito (repetições, séries, duração, dificuldade, frequência) com base em feedback do paciente. Registra histórico de alterações."
)
def update_prescription(
    prescription_id: int,
    prescription_data: PrescriptionUpdateRequest,
    physiotherapist_id: int = Query(..., description="ID do fisioterapeuta que está fazendo a alteração"),
    session: Session = Depends(get_session)
):
    """Atualiza uma prescrição e registra no histórico
    
    Os novos parâmetros serão refletidos imediatamente para o paciente.
    """
    # Extrair apenas os dados de atualização da prescrição (excluindo change_reason)
    update_dict = prescription_data.model_dump(exclude_unset=True)
    change_reason = update_dict.pop("change_reason", None)
    
    # Criar objeto de atualização com apenas os campos fornecidos
    update_data = PrescriptionUpdate(**update_dict)
    
    prescription = PrescriptionService.update_prescription(
        session,
        prescription_id,
        update_data,
        physiotherapist_id=physiotherapist_id,
        change_reason=change_reason
    )
    
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prescrição com ID {prescription_id} não encontrada"
        )
    
    # Enriquecer resposta
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


@router.get(
    "/prescriptions/{prescription_id}/history",
    response_model=List[PrescriptionHistoryResponse],
    summary="Obtém histórico de alterações de uma prescrição",
    description="Retorna todas as alterações feitas nos parâmetros da prescrição, incluindo quem alterou e quando"
)
def get_prescription_history(
    prescription_id: int,
    session: Session = Depends(get_session)
):
    """Lista histórico de alterações de uma prescrição"""
    # Verificar se a prescrição existe
    prescription = PrescriptionService.get_prescription(session, prescription_id)
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prescrição com ID {prescription_id} não encontrada"
        )
    
    history = PrescriptionService.get_prescription_history(session, prescription_id)
    
    # Enriquecer com dados do fisioterapeuta
    from app.models.physiotherapist import Physiotherapist
    result = []
    for entry in history:
        physiotherapist = session.get(Physiotherapist, entry.physiotherapist_id)
        
        history_response = PrescriptionHistoryResponse(
            id=entry.id,
            prescription_id=entry.prescription_id,
            physiotherapist_id=entry.physiotherapist_id,
            old_repetitions=entry.old_repetitions,
            old_series=entry.old_series,
            old_duration_minutes=entry.old_duration_minutes,
            old_difficulty_level=entry.old_difficulty_level,
            old_weekly_frequency=entry.old_weekly_frequency,
            new_repetitions=entry.new_repetitions,
            new_series=entry.new_series,
            new_duration_minutes=entry.new_duration_minutes,
            new_difficulty_level=entry.new_difficulty_level,
            new_weekly_frequency=entry.new_weekly_frequency,
            change_reason=entry.change_reason,
            changed_at=entry.changed_at,
            changed_by=physiotherapist,
        )
        result.append(history_response)
    
    return result


@router.get(
    "/patients/{patient_id}/exercises/today",
    response_model=List[PrescriptionResponse],
    summary="Lista exercícios recomendados para o paciente no dia atual",
    description="Retorna os exercícios que o paciente deve fazer hoje, incluindo detalhes completos do exercício (descrição, instruções, mídia demonstrativa, parâmetros)"
)
def get_today_exercises(patient_id: int, session: Session = Depends(get_session)):
    """Lista exercícios recomendados para o paciente no dia atual
    
    Retorna prescrições que:
    - Têm data agendada para hoje OU
    - São prescrições ativas sem data específica (plano regular)
    
    Caso não haja exercícios, retorna erro 404 com mensagem clara.
    """
    prescriptions = PrescriptionService.get_prescriptions_for_today(session, patient_id)
    
    if not prescriptions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum exercício recomendado para hoje"
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
