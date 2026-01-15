from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.database import get_session
from app.services.report_service import ReportService
from app.schemas.report import ReportRequest, ReportResponse

router = APIRouter()


@router.post(
    "/reports",
    response_model=ReportResponse,
    summary="Gera relatório detalhado do progresso do paciente",
    description="Gera um relatório completo com dados de execução, taxa de conclusão, níveis de dor, feedbacks e indicadores de progresso. Permite filtrar por período (última semana, último mês, últimos 3 meses ou período customizado)"
)
def generate_report(
    request: ReportRequest,
    session: Session = Depends(get_session)
):
    """
    Gera relatório detalhado do progresso do paciente.
    
    O relatório inclui:
    - Datas de execução dos exercícios
    - Exercícios realizados
    - Taxa de conclusão
    - Níveis de dor relatados
    - Feedbacks relevantes
    - Indicadores de progresso e evolução
    
    Se não houver dados suficientes no período, o campo 'has_data' será False
    e uma mensagem adequada será retornada.
    """
    try:
        report = ReportService.generate_report(session, request)
        
        if not report.has_data:
            # Retornar relatório vazio com mensagem
            return report
        
        return report
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/patients/{patient_id}/reports",
    response_model=ReportResponse,
    summary="Obtém relatório do paciente pela ficha",
    description="Acesso ao relatório do paciente através da ficha do paciente. Usa o período padrão (último mês)"
)
def get_patient_report(
    patient_id: int,
    period_filter: str = "last_month",
    start_date: str = None,
    end_date: str = None,
    session: Session = Depends(get_session)
):
    """
    Obtém relatório do paciente pela ficha.
    
    Esta rota permite acessar o relatório diretamente pela ficha do paciente.
    """
    from datetime import datetime
    from app.schemas.report import PeriodFilter
    
    try:
        # Converter strings de data para datetime se fornecidas
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        request = ReportRequest(
            patient_id=patient_id,
            period_filter=PeriodFilter(period_filter),
            start_date=start_dt,
            end_date=end_dt,
        )
        
        report = ReportService.generate_report(session, request)
        return report
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )