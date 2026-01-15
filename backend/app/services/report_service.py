from sqlmodel import Session, select, func
from typing import List, Tuple
from datetime import datetime, timedelta
from app.models.patient import Patient
from app.models.exercise_execution import ExerciseExecution
from app.models.prescription import Prescription
from app.models.pain_level import PainLevel
from app.models.feedback import Feedback
from app.schemas.report import (
    ReportRequest,
    ReportResponse,
    ExerciseExecutionDetail,
    ProgressIndicator,
    PeriodFilter,
)


class ReportService:
    """Serviço para gerenciar relatórios de pacientes"""

    @staticmethod
    def _calculate_period(request: ReportRequest) -> Tuple[datetime, datetime]:
        """Calcula o período baseado no filtro"""
        now = datetime.utcnow()
        
        if request.period_filter == PeriodFilter.LAST_WEEK:
            start = now - timedelta(days=7)
            end = now
        elif request.period_filter == PeriodFilter.LAST_MONTH:
            start = now - timedelta(days=30)
            end = now
        elif request.period_filter == PeriodFilter.LAST_3_MONTHS:
            start = now - timedelta(days=90)
            end = now
        elif request.period_filter == PeriodFilter.CUSTOM:
            if not request.start_date or not request.end_date:
                raise ValueError("start_date e end_date são obrigatórios para período customizado")
            start = request.start_date
            end = request.end_date
        else:
            start = now - timedelta(days=30)
            end = now
        
        return start, end

    @staticmethod
    def generate_report(session: Session, request: ReportRequest) -> ReportResponse:
        """Gera relatório detalhado do paciente"""
        # Verificar se o paciente existe
        patient = session.get(Patient, request.patient_id)
        if not patient:
            raise ValueError(f"Paciente com ID {request.patient_id} não encontrado")
        
        # Calcular período
        period_start, period_end = ReportService._calculate_period(request)
        
        # Buscar execuções no período
        statement = (
            select(ExerciseExecution)
            .where(ExerciseExecution.patient_id == request.patient_id)
            .where(ExerciseExecution.execution_date >= period_start)
            .where(ExerciseExecution.execution_date <= period_end)
            .order_by(ExerciseExecution.execution_date.desc())
        )
        
        executions = list(session.exec(statement).all())
        
        # Buscar prescrições ativas do paciente
        prescriptions_statement = (
            select(Prescription)
            .where(Prescription.patient_id == request.patient_id)
            .where(Prescription.is_active == True)
        )
        prescriptions = list(session.exec(prescriptions_statement).all())
        
        # Preparar detalhes das execuções
        from app.models.exercise_library import ExerciseLibrary
        from app.schemas.report import ExerciseLibraryBasic

        execution_details = []
        for execution in executions:
            # Buscar exercício relacionado
            prescription = session.get(Prescription, execution.prescription_id)
            exercise = None
            if prescription:
                exercise_lib = session.get(ExerciseLibrary, prescription.exercise_id)
                if exercise_lib:
                    exercise = ExerciseLibraryBasic(
                        id=exercise_lib.id,
                        name=exercise_lib.name,
                        category=exercise_lib.category,
                    )

            # Buscar níveis de dor
            from app.schemas.report import PainLevelDetail, FeedbackDetail
            pain_levels_statement = (
                select(PainLevel)
                .where(PainLevel.execution_id == execution.id)
            )
            pain_levels_data = list(session.exec(pain_levels_statement).all())
            pain_levels = [
                PainLevelDetail(
                    id=p.id,
                    pain_level=p.pain_level,
                    pain_location=p.pain_location,
                    notes=p.notes,
                    reported_at=p.reported_at,
                )
                for p in pain_levels_data
            ]

            # Buscar feedbacks
            feedbacks_statement = (
                select(Feedback)
                .where(Feedback.execution_id == execution.id)
            )
            feedbacks_data = list(session.exec(feedbacks_statement).all())
            feedbacks = [
                FeedbackDetail(
                    id=f.id,
                    feedback_type=f.feedback_type,
                    content=f.content,
                    is_positive=f.is_positive,
                    created_at=f.created_at,
                )
                for f in feedbacks_data
            ]

            execution_detail = ExerciseExecutionDetail(
                id=execution.id,
                execution_date=execution.execution_date,
                repetitions_completed=execution.repetitions_completed,
                series_completed=execution.series_completed,
                duration_minutes=execution.duration_minutes,
                completion_rate=execution.completion_rate,
                was_completed=execution.was_completed,
                exercise=exercise,
                pain_levels=pain_levels,
                feedbacks=feedbacks,
            )
            execution_details.append(execution_detail)

        # Listar exercícios prescritos (ativos)
        prescribed_exercises = []
        seen_exercise_ids = set()
        for prescription in prescriptions:
            exercise_lib = session.get(ExerciseLibrary, prescription.exercise_id)
            if exercise_lib and exercise_lib.id not in seen_exercise_ids:
                prescribed_exercises.append(
                    ExerciseLibraryBasic(
                        id=exercise_lib.id,
                        name=exercise_lib.name,
                        category=exercise_lib.category,
                    )
                )
                seen_exercise_ids.add(exercise_lib.id)

        # Calcular indicadores de progresso
        progress = ReportService._calculate_progress(
            session, executions, prescriptions, period_start, period_end
        )

        has_data = len(executions) > 0

        return ReportResponse(
            patient_id=patient.id,
            patient_name=patient.name,
            period_start=period_start,
            period_end=period_end,
            generated_at=datetime.utcnow(),
            executions=execution_details,
            progress=progress,
            has_data=has_data,
            prescribed_exercises=prescribed_exercises,
        )

    @staticmethod
    def _calculate_progress(
        session: Session,
        executions: List[ExerciseExecution],
        prescriptions: List[Prescription],
        period_start: datetime,
        period_end: datetime,
    ) -> ProgressIndicator:
        """Calcula indicadores de progresso"""
        total_executions = len(executions)
        
        if total_executions == 0:
            return ProgressIndicator(
                total_executions=0,
                completion_rate_avg=0.0,
                pain_level_avg=None,
                exercises_completed=0,
                exercises_prescribed=len(prescriptions),
                adherence_rate=0.0,
            )
        
        # Taxa média de conclusão
        completion_rates = [e.completion_rate for e in executions if e.completion_rate is not None]
        completion_rate_avg = sum(completion_rates) / len(completion_rates) if completion_rates else 0.0
        
        # Nível médio de dor
        pain_levels = []
        for execution in executions:
            pain_statement = select(PainLevel).where(PainLevel.execution_id == execution.id)
            pain_records = list(session.exec(pain_statement).all())
            pain_levels.extend([p.pain_level for p in pain_records])
        
        pain_level_avg = sum(pain_levels) / len(pain_levels) if pain_levels else None
        
        # Exercícios completados
        exercises_completed = sum(1 for e in executions if e.was_completed)
        
        # Taxa de aderência (execuções realizadas vs esperadas)
        exercises_prescribed = len(prescriptions)
        expected_executions = 0
        for prescription in prescriptions:
            # Calcular quantas execuções eram esperadas no período
            days_in_period = (period_end - period_start).days
            weeks_in_period = days_in_period / 7
            expected_executions += int(weeks_in_period * prescription.weekly_frequency)
        
        adherence_rate = (
            (total_executions / expected_executions * 100) if expected_executions > 0 else 0.0
        )
        
        return ProgressIndicator(
            total_executions=total_executions,
            completion_rate_avg=round(completion_rate_avg, 2),
            pain_level_avg=round(pain_level_avg, 2) if pain_level_avg else None,
            exercises_completed=exercises_completed,
            exercises_prescribed=exercises_prescribed,
            adherence_rate=round(adherence_rate, 2),
        )
