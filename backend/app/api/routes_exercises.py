from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from app.core.database import get_session
from app.services.exercise_service import ExerciseService
from app.schemas.exercise import (
    ExerciseCreate,
    ExerciseResponse,
    ExerciseSuccessResponse,
    ExerciseUpdate
)
from app.models.exercise_library import ExerciseLibrary

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
    # Converter cada ExerciseLibrary para ExerciseResponse
    return [ExerciseResponse.model_validate(exercise) for exercise in exercises]

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
    # Converter ExerciseLibrary para ExerciseResponse
    return ExerciseResponse.model_validate(exercise)

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
        
        # Converter ExerciseLibrary para ExerciseResponse
        exercise_response = ExerciseResponse.model_validate(exercise)
        
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
