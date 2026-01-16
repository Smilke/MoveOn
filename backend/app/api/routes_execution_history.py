from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from typing import Optional
from datetime import datetime

from app.core.database import get_session
from app.services.execution_history_service import ExecutionHistoryService
from app.schemas.execution_history import (
    ExecutionHistoryResponse,
    ExecutionHistoryResponse,
    PeriodFilter,
    ExecutionCreate
)
from app.models.patient import Patient  
router = APIRouter()


@router.post(
    "/executions",
    status_code=status.HTTP_201_CREATED,
    summary="Registra uma execução de exercício",
    description="Salva o histórico de execução de um exercício realizado pelo paciente"
)
def create_execution(
    execution_data: ExecutionCreate,
    session: Session = Depends(get_session)
):
    """Registra uma execução"""
    try:
        execution = ExecutionHistoryService.create_execution(session, execution_data)
        return {"message": "Execução registrada com sucesso", "id": execution.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao registrar execução: {str(e)}")


@router.get(
    "/patients/{patient_id}/exercise-history",
    response_model=ExecutionHistoryResponse,
    summary="Obtém histórico de execução de exercícios de um paciente",
    description="Retorna a lista de sessões de execução de exercícios de um paciente, com filtros de período opcionais"
)
def get_execution_history(
    patient_id: int,
    period_filter: PeriodFilter = Query(
        default=PeriodFilter.LAST_7_DAYS,
        description="Filtro de período pré-definido"
    ),
    start_date: Optional[datetime] = Query(
        default=None,
        description="Data de início (obrigatório se period_filter for 'custom')"
    ),
    end_date: Optional[datetime] = Query(
        default=None,
        description="Data de fim (obrigatório se period_filter for 'custom')"
    ),
    session: Session = Depends(get_session)
):
    """
    Obtém o histórico de execução de exercícios de um paciente.

    - Se o paciente **não existir**, retorna 404.
    - Se existir, retorna o histórico no período escolhido
      (ou mensagem avisando que não há dados).
    """
    # Verifica se o paciente existe no banco
    paciente = session.get(Patient, patient_id)
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente com ID {patient_id} não encontrado."
        )

    # Busca o histórico
    try:
        history_items, period_start, period_end, total_executions = (
            ExecutionHistoryService.get_execution_history_summary(
                session=session,
                patient_id=patient_id,
                period_filter=period_filter,
                start_date=start_date,
                end_date=end_date
            )
        )

        has_data = total_executions > 0

        response = ExecutionHistoryResponse(
            patient_id=patient_id,
            period_start=period_start,
            period_end=period_end,
            total_executions=total_executions,
            executions=history_items,
            has_data=has_data,
            message=None if has_data else "Ainda não foram registrados exercícios para este período."
        )

        return response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar histórico de execução: {str(e)}"
        )