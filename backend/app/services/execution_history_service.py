from sqlmodel import Session, select, func, and_, or_
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from app.models.exercise_execution import ExerciseExecution
from app.models.prescription import Prescription
from app.models.exercise_library import ExerciseLibrary
from app.models.pain_level import PainLevel
from app.schemas.execution_history import (
    ExecutionHistoryItem,
    ExecutionStatus,
    ExecutionHistoryItem,
    ExecutionStatus,
    PeriodFilter,
    ExecutionCreate
)
from app.models.feedback import Feedback


class ExecutionHistoryService:
    """Serviço para gerenciar histórico de execução de exercícios"""

    @staticmethod
    def _get_status_from_completion_rate(completion_rate: float, was_completed: bool) -> ExecutionStatus:
        """Determina o status baseado na taxa de conclusão"""
        if was_completed or completion_rate >= 100.0:
            return ExecutionStatus.COMPLETED
        elif completion_rate >= 50.0:
            return ExecutionStatus.PARTIAL
        else:
            return ExecutionStatus.NOT_COMPLETED

    @staticmethod
    def _calculate_period_dates(period_filter: PeriodFilter, start_date: Optional[datetime], end_date: Optional[datetime]) -> Tuple[datetime, datetime]:
        """Calcula as datas de início e fim baseado no filtro de período"""
        now = datetime.utcnow()
        
        if period_filter == PeriodFilter.LAST_7_DAYS:
            end = now
            start = now - timedelta(days=7)
        elif period_filter == PeriodFilter.LAST_MONTH:
            end = now
            start = now - timedelta(days=30)
        elif period_filter == PeriodFilter.CUSTOM:
            if not start_date or not end_date:
                raise ValueError("Para filtro customizado, start_date e end_date são obrigatórios")
            start = start_date
            end = end_date
        else:
            # Padrão: últimos 7 dias
            end = now
            start = now - timedelta(days=7)
        
        return start, end

    @staticmethod
    def get_execution_history(
        session: Session,
        patient_id: int,
        period_filter: PeriodFilter = PeriodFilter.LAST_7_DAYS,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[ExecutionHistoryItem]:
        """Obtém o histórico de execução de exercícios de um paciente"""
        try:
            # Calcular período
            period_start, period_end = ExecutionHistoryService._calculate_period_dates(
                period_filter, start_date, end_date
            )
            
            # Buscar execuções do paciente no período
            statement = select(ExerciseExecution).where(
                and_(
                    ExerciseExecution.patient_id == patient_id,
                    ExerciseExecution.execution_date >= period_start,
                    ExerciseExecution.execution_date <= period_end
                )
            ).order_by(ExerciseExecution.execution_date.desc())
            
            executions = list(session.exec(statement).all())
            
            # Transformar em ExecutionHistoryItem
            history_items = []
            for execution in executions:
                # Buscar exercício relacionado através da prescrição
                prescription = session.get(Prescription, execution.prescription_id)
                exercise = None
                if prescription:
                    exercise_model = session.get(ExerciseLibrary, prescription.exercise_id)
                    if exercise_model:
                        from app.schemas.execution_history import ExerciseBasicInfo
                        exercise = ExerciseBasicInfo(
                            id=exercise_model.id,
                            name=exercise_model.name,
                            category=exercise_model.category
                        )
                
                # Buscar nível de dor mais recente da execução
                pain_statement = select(PainLevel).where(
                    PainLevel.execution_id == execution.id
                ).order_by(PainLevel.reported_at.desc()).limit(1)
                
                pain_level_model = session.exec(pain_statement).first()
                pain_level = None
                if pain_level_model:
                    from app.schemas.execution_history import PainLevelInfo
                    pain_level = PainLevelInfo(
                        pain_level=pain_level_model.pain_level,
                        pain_location=pain_level_model.pain_location,
                        reported_at=pain_level_model.reported_at
                    )
                
                # Determinar status
                status = ExecutionHistoryService._get_status_from_completion_rate(
                    execution.completion_rate,
                    execution.was_completed
                )
                
                if exercise:  # Só adiciona se tiver exercício
                    history_item = ExecutionHistoryItem(
                        id=execution.id,
                        execution_date=execution.execution_date,
                        exercise=exercise,
                        status=status,
                        completion_rate=execution.completion_rate,
                        repetitions_completed=execution.repetitions_completed,
                        series_completed=execution.series_completed,
                        duration_minutes=execution.duration_minutes,
                        pain_level=pain_level
                    )
                    history_items.append(history_item)
            
            return history_items
            
        except Exception as e:
            raise ValueError(f"Erro ao buscar histórico de execução: {str(e)}")

    @staticmethod
    def get_execution_history_summary(
        session: Session,
        patient_id: int,
        period_filter: PeriodFilter = PeriodFilter.LAST_7_DAYS,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Tuple[List[ExecutionHistoryItem], datetime, datetime, int]:
        """Obtém o histórico e informações resumidas"""
        period_start, period_end = ExecutionHistoryService._calculate_period_dates(
            period_filter, start_date, end_date
        )
        
        history_items = ExecutionHistoryService.get_execution_history(
            session, patient_id, period_filter, start_date, end_date
        )
        
        total_executions = len(history_items)
        
        return history_items, period_start, period_end, total_executions

    @staticmethod
    def create_execution(
        session: Session,
        data: ExecutionCreate
    ) -> ExerciseExecution:
        """Registra uma nova execução de exercício"""
        # 1. Buscar a prescrição para validar e pegar dados
        prescription = session.get(Prescription, data.prescription_id)
        if not prescription:
            raise ValueError("Prescrição não encontrada")

        # 2. Calcular taxa de conclusão (simplificado)
        # Se completou o que foi pedido, 100%. Se não, regra de 3.
        # Aqui vamos assumir que completion_rate vem calculado ou é 100% se marcado como completo
        completion_rate = 100.0 if data.was_completed else 0.0
        
        # Se quiser algo mais refinado:
        if prescription.series > 0 and data.series_completed > 0:
             calc = (data.series_completed / prescription.series) * 100
             if calc > 100: calc = 100.0
             if calc > completion_rate: completion_rate = calc

        # 3. Criar Execução
        execution = ExerciseExecution(
            prescription_id=data.prescription_id,
            patient_id=prescription.patient_id,
            repetitions_completed=data.repetitions_completed,
            series_completed=data.series_completed,
            duration_minutes=data.duration_minutes,
            completion_rate=completion_rate,
            was_completed=data.was_completed,
            execution_date=datetime.utcnow()
        )
        session.add(execution)
        session.commit()
        session.refresh(execution)

        # 4. Registrar Nível de Dor (se houver)
        if data.pain_level is not None:
            pain = PainLevel(
                execution_id=execution.id,
                pain_level=data.pain_level,
                reported_at=datetime.utcnow()
            )
            session.add(pain)

        # 5. Registrar Feedback (se houver)
        if data.feedback_comment:
            fb = Feedback(
                execution_id=execution.id,
                patient_id=prescription.patient_id,
                content=data.feedback_comment,
                feedback_type="neutral", # default
                is_positive=True
            )
            session.add(fb)
        
        session.commit()
        session.refresh(execution)
        return execution
