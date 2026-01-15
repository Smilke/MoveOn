from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from typing import Optional
from datetime import datetime

from app.core.database import get_session
from app.services.progress_report_service import ProgressReportService
from app.schemas.progress_report import (
    ProgressReportResponse,
    PeriodFilter
)


router = APIRouter()


@router.get(
    "/patients/{patient_id}/progress-report",
    response_model=ProgressReportResponse,
    summary="Gera relatório detalhado de progresso do paciente",
    description="Retorna um relatório com visão simplificada e compreensível do progresso do paciente, incluindo dias com exercício, tempo de atividade, evolução da dor e metas alcançadas"
)
def get_progress_report(
    patient_id: int,
    period_filter: PeriodFilter = Query(
        default=PeriodFilter.LAST_MONTH,
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
    Gera relatório detalhado de progresso do paciente.
    
    O relatório inclui:
    - Dias em que fez exercício
    - Tempo total de atividade
    - Taxa média de conclusão
    - Evolução da dor ao longo do período
    - Progresso por exercício
    - Metas alcançadas
    
    Se não houver dados suficientes, retorna uma mensagem informativa.
    """
    try:
        report = ProgressReportService.generate_progress_report(
            session=session,
            patient_id=patient_id,
            period_filter=period_filter,
            start_date=start_date,
            end_date=end_date
        )
        
        return report
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar relatório de progresso: {str(e)}"
        )
