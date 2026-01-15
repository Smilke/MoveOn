from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List

from app.core.database import get_session
from app.services.prescription_service import PrescriptionService
from app.schemas.prescription import (
    ExercisePrescriptionRequest,
    PrescriptionResponse,
    PrescriptionSuccessResponse,
)
from app.schemas.prescription import PrescriptionUpdate, ExerciseLibraryInfo
from app.models.exercise_library import ExerciseLibrary
from app.models.prescription import Prescription
from app.models.patient import Patient
from app.models.exercise_execution import ExerciseExecution
from app.models.exercise_example_video import ExerciseExampleVideo

router = APIRouter()


_DELETED_PLACEHOLDER_NOTES = "__deleted_placeholder__"


def _exercise_info_with_video(session: Session, exercise_id: int):
    exercise = session.get(ExerciseLibrary, exercise_id)
    if not exercise:
        return None

    info = ExerciseLibraryInfo.model_validate(exercise)
    v = session.exec(
        select(ExerciseExampleVideo).where(ExerciseExampleVideo.exercise_id == exercise_id)
    ).first()
    if v:
        info.example_video_filename = v.filename
        info.example_video_url = f"/exercise-videos/{v.filename}"
    return info


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
        exercise = _exercise_info_with_video(session, prescription.exercise_id)
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
        if prescription.notes == _DELETED_PLACEHOLDER_NOTES:
            continue
        exercise = _exercise_info_with_video(session, prescription.exercise_id)
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
    exercise = _exercise_info_with_video(session, prescription.exercise_id)
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
    response_model=PrescriptionSuccessResponse,
    summary="Atualiza uma prescrição",
    description="Atualiza uma prescrição existente. O physiotherapist_id deve ser fornecido como query parameter (em produção viria do token)."
)
def update_prescription(
    prescription_id: int,
    prescription_data: PrescriptionUpdate,
    physiotherapist_id: int = Query(..., description="ID do fisioterapeuta (em produção viria do token)"),
    session: Session = Depends(get_session),
):
    prescription = PrescriptionService.get_prescription(session, prescription_id)
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prescrição com ID {prescription_id} não encontrada",
        )
    if prescription.physiotherapist_id != physiotherapist_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: prescrição não pertence a este fisioterapeuta",
        )

    updated = PrescriptionService.update_prescription(session, prescription_id, prescription_data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prescrição com ID {prescription_id} não encontrada",
        )

    exercise = _exercise_info_with_video(session, updated.exercise_id)
    patient = session.get(Patient, updated.patient_id)
    prescription_response = PrescriptionResponse(
        id=updated.id,
        patient_id=updated.patient_id,
        physiotherapist_id=updated.physiotherapist_id,
        exercise_id=updated.exercise_id,
        repetitions=updated.repetitions,
        series=updated.series,
        duration_minutes=updated.duration_minutes,
        difficulty_level=updated.difficulty_level,
        weekly_frequency=updated.weekly_frequency,
        is_active=updated.is_active,
        notes=updated.notes,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
        exercise=exercise,
        patient=patient,
    )

    return PrescriptionSuccessResponse(
        message="Prescrição atualizada com sucesso",
        prescription=prescription_response,
    )


@router.get(
    "/physiotherapists/{physio_id}/patients/{patient_id}/prescriptions",
    response_model=List[PrescriptionResponse],
    summary="Lista prescrições de um paciente feitas por um fisioterapeuta",
    description="Retorna as prescrições de um paciente filtradas pelo fisioterapeuta. Requer que o paciente esteja vinculado ao fisioterapeuta."
)
def get_physio_patient_prescriptions(
    physio_id: int,
    patient_id: int,
    active_only: bool = False,
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

    statement = select(Prescription).where(
        Prescription.patient_id == patient_id,
        Prescription.physiotherapist_id == physio_id,
    )
    if active_only:
        statement = statement.where(Prescription.is_active == True)
    prescriptions = list(session.exec(statement.order_by(Prescription.created_at.desc())).all())

    result: List[PrescriptionResponse] = []
    for prescription in prescriptions:
        if prescription.notes == _DELETED_PLACEHOLDER_NOTES:
            continue
        exercise = _exercise_info_with_video(session, prescription.exercise_id)
        result.append(
            PrescriptionResponse(
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
        )

    return result


@router.delete(
    "/physiotherapists/{physio_id}/patients/{patient_id}/prescriptions/{prescription_id}",
    status_code=status.HTTP_200_OK,
    summary="Desativa (remove) uma prescrição",
    description="Soft delete de uma prescrição (is_active=false). Verifica vínculo paciente-fisio e pertencimento da prescrição.",
)
def deactivate_prescription_for_physio_patient(
    physio_id: int,
    patient_id: int,
    prescription_id: int,
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

    prescription = session.get(Prescription, prescription_id)
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prescrição com ID {prescription_id} não encontrada",
        )
    if prescription.patient_id != patient_id or prescription.physiotherapist_id != physio_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: prescrição não pertence a este paciente/fisioterapeuta",
        )

    ok = PrescriptionService.delete_prescription(session, prescription_id)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prescrição com ID {prescription_id} não encontrada",
        )

    return {"message": "Prescrição removida (desativada) com sucesso"}


@router.patch(
    "/physiotherapists/{physio_id}/patients/{patient_id}/prescriptions/{prescription_id}/reactivate",
    status_code=status.HTTP_200_OK,
    summary="Reativa uma prescrição desativada",
    description="Reativa (is_active=true) uma prescrição anteriormente desativada. Verifica vínculo paciente-fisio e pertencimento da prescrição.",
)
def reactivate_prescription_for_physio_patient(
    physio_id: int,
    patient_id: int,
    prescription_id: int,
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

    prescription = session.get(Prescription, prescription_id)
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prescrição com ID {prescription_id} não encontrada",
        )
    if prescription.patient_id != patient_id or prescription.physiotherapist_id != physio_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: prescrição não pertence a este paciente/fisioterapeuta",
        )

    prescription.is_active = True
    session.add(prescription)
    session.commit()

    return {"message": "Prescrição reativada com sucesso"}


@router.delete(
    "/physiotherapists/{physio_id}/patients/{patient_id}/prescriptions/{prescription_id}/permanent",
    status_code=status.HTTP_200_OK,
    summary="Remove permanentemente uma prescrição (somente se sem histórico)",
    description="Hard delete. Só permite remover se não houver execuções vinculadas (para preservar histórico).",
)
def permanently_delete_prescription_for_physio_patient(
    physio_id: int,
    patient_id: int,
    prescription_id: int,
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

    prescription = session.get(Prescription, prescription_id)
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prescrição com ID {prescription_id} não encontrada",
        )
    if prescription.patient_id != patient_id or prescription.physiotherapist_id != physio_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: prescrição não pertence a este paciente/fisioterapeuta",
        )

    try:
        executions = list(
            session.exec(
                select(ExerciseExecution).where(ExerciseExecution.prescription_id == prescription_id)
            ).all()
        )

        if executions:
            placeholder = Prescription(
                patient_id=prescription.patient_id,
                physiotherapist_id=prescription.physiotherapist_id,
                exercise_id=prescription.exercise_id,
                repetitions=prescription.repetitions,
                series=prescription.series,
                duration_minutes=prescription.duration_minutes,
                difficulty_level=prescription.difficulty_level,
                weekly_frequency=prescription.weekly_frequency,
                is_active=False,
                notes=_DELETED_PLACEHOLDER_NOTES,
            )
            session.add(placeholder)
            session.flush()

            for ex in executions:
                ex.prescription_id = placeholder.id
                session.add(ex)

        session.delete(prescription)
        session.commit()
        return {"message": "Prescrição removida permanentemente"}
    except Exception as e:
        if session.in_transaction():
            session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover permanentemente: {str(e)}",
        )
