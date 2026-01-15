from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlmodel import Session, select
from typing import List
from pathlib import Path
import uuid

from app.core.database import get_session
from app.services.exercise_service import ExerciseService
from app.schemas.exercise import (
    ExerciseCreate,
    ExerciseResponse,
    ExerciseSuccessResponse,
    ExerciseUpdate
)
from app.models.exercise_library import ExerciseLibrary
from app.models.exercise_example_video import ExerciseExampleVideo

router = APIRouter()

@router.get(
    "/exercises",
    response_model=List[ExerciseResponse],
    summary="Lista todos os exercícios gamificados disponíveis",
    description="Retorna a biblioteca completa de exercícios gamificados disponíveis para prescrição"
)
def list_exercises(
    active_only: bool = True,
    session: Session = Depends(get_session)
):
    """Lista todos os exercícios da biblioteca"""
    exercises = ExerciseService.get_all_exercises(session, active_only=active_only)

    responses = [ExerciseResponse.model_validate(exercise) for exercise in exercises]

    if responses:
        ids = [ex.id for ex in responses]
        vids = session.exec(
            select(ExerciseExampleVideo).where(ExerciseExampleVideo.exercise_id.in_(ids))
        ).all()
        by_ex_id = {v.exercise_id: v for v in vids}
        for ex in responses:
            v = by_ex_id.get(ex.id)
            if v:
                ex.example_video_filename = v.filename
                ex.example_video_url = f"/exercise-videos/{v.filename}"

    return responses

@router.post(
    "/exercises",
    response_model=ExerciseSuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria um exercícios gamificado no banco de dados",
    description="Permite a criação de um exercício detalhado para o fisioterapeuta usar com um paciente."
)
def create_exercise(
    exercise_data: ExerciseCreate,
    session: Session = Depends(get_session)
):
    """
    Cria um novo exercício na biblioteca.
    """
    try:
        # Criar o exercício no banco de dados
        exercise = ExerciseService.create_exercise(session, exercise_data)
        
        # Converter ExerciseLibrary para ExerciseResponse
        # O model_validate funciona porque ExerciseLibrary é um SQLModel que herda de Pydantic
        exercise_response = ExerciseResponse.model_validate(exercise)
        
        return ExerciseSuccessResponse(
            message="Exercício criado com sucesso",
            exercise=exercise_response
        )
    except ValueError as e:
        if session.in_transaction():
            session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        # Re-raise HTTP exceptions sem modificação
        raise
    except Exception as e:
        if session.in_transaction():
            session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar exercício: {str(e)}"
        )

@router.get(
    "/exercises/{exercise_id}",
    response_model=ExerciseResponse,
    summary="Obtém detalhes de um exercício específico",
    description="Retorna os detalhes de um exercício gamificado da biblioteca"
)
def get_exercise(
    exercise_id: int,
    session: Session = Depends(get_session)
):
    """Obtém um exercício específico"""
    exercise = ExerciseService.get_exercise(session, exercise_id)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercício com ID {exercise_id} não encontrado"
        )
    response = ExerciseResponse.model_validate(exercise)
    v = session.exec(
        select(ExerciseExampleVideo).where(ExerciseExampleVideo.exercise_id == exercise_id)
    ).first()
    if v:
        response.example_video_filename = v.filename
        response.example_video_url = f"/exercise-videos/{v.filename}"
    return response

@router.put(
    "/exercises/{exercise_id}",
    response_model=ExerciseSuccessResponse,
    summary="Atualiza um exercício existente",
    description="Atualiza os dados de um exercício da biblioteca"
)
def update_exercise(
    exercise_id: int,
    exercise_data: ExerciseUpdate,
    session: Session = Depends(get_session)
):
    """Atualiza um exercício"""
    try:
        exercise = ExerciseService.update_exercise(session, exercise_id, exercise_data)
        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exercício com ID {exercise_id} não encontrado"
            )
        
        exercise_response = ExerciseResponse.model_validate(exercise)

        v = session.exec(
            select(ExerciseExampleVideo).where(ExerciseExampleVideo.exercise_id == exercise_id)
        ).first()
        if v:
            exercise_response.example_video_filename = v.filename
            exercise_response.example_video_url = f"/exercise-videos/{v.filename}"
        
        return ExerciseSuccessResponse(
            message="Exercício atualizado com sucesso",
            exercise=exercise_response
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar exercício: {str(e)}"
        )


@router.delete(
    "/exercises/{exercise_id}",
    status_code=status.HTTP_200_OK,
    summary="Remove (desativa) um exercício",
    description="Soft delete: marca o exercício como inativo (is_active=false) para não aparecer mais para prescrição/execução."
)
def delete_exercise(
    exercise_id: int,
    session: Session = Depends(get_session)
):
    try:
        ok = ExerciseService.delete_exercise(session, exercise_id)
        if not ok:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exercício com ID {exercise_id} não encontrado"
            )
        return {"message": "Exercício removido (desativado) com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/exercises/{exercise_id}/example-video",
    status_code=status.HTTP_200_OK,
    summary="Envia vídeo de exemplo do exercício",
    description="Faz upload de um vídeo de exemplo para um exercício e registra a referência."
)
async def upload_exercise_example_video(
    exercise_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    exercise = session.get(ExerciseLibrary, exercise_id)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercício com ID {exercise_id} não encontrado"
        )

    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".mp4", ".mov", ".webm", ".mkv", ".avi"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de vídeo inválido. Use mp4/mov/webm/mkv/avi."
        )

    uploads_dir = Path(__file__).resolve().parents[1] / "uploads" / "exercise_example_videos"
    uploads_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}{suffix}"
    dest = uploads_dir / filename
    content = await file.read()
    dest.write_bytes(content)

    existing = session.exec(
        select(ExerciseExampleVideo).where(ExerciseExampleVideo.exercise_id == exercise_id)
    ).first()
    if existing:
        existing.filename = filename
        session.add(existing)
    else:
        session.add(ExerciseExampleVideo(exercise_id=exercise_id, filename=filename))

    session.commit()

    return {
        "message": "Vídeo de exemplo enviado com sucesso",
        "exercise_id": exercise_id,
        "example_video_filename": filename,
        "example_video_url": f"/exercise-videos/{filename}",
    }
