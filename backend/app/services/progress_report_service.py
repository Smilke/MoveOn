from sqlmodel import Session, select, func, and_, or_
from typing import List, Optional, Tuple, Dict
from datetime import datetime, timedelta
from collections import defaultdict
from app.models.exercise_execution import ExerciseExecution
from app.models.prescription import Prescription
from app.models.exercise_library import ExerciseLibrary
from app.models.pain_level import PainLevel
from app.models.patient import Patient
from app.schemas.progress_report import (
    PeriodFilter,
    PainEvolutionItem,
    ExerciseProgress,
    GoalAchievement,
    ProgressReportResponse
)


class ProgressReportService:
    """Serviço para gerar relatórios de progresso do paciente"""

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
        elif period_filter == PeriodFilter.LAST_3_MONTHS:
            end = now
            start = now - timedelta(days=90)
        elif period_filter == PeriodFilter.CUSTOM:
            if not start_date or not end_date:
                raise ValueError("Para filtro customizado, start_date e end_date são obrigatórios")
            start = start_date
            end = end_date
        else:
            # Padrão: último mês
            end = now
            start = now - timedelta(days=30)
        
        return start, end

    @staticmethod
    def generate_progress_report(
        session: Session,
        patient_id: int,
        period_filter: PeriodFilter = PeriodFilter.LAST_MONTH,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> ProgressReportResponse:
        """Gera relatório detalhado de progresso do paciente"""
        try:
            # Verificar se paciente existe
            patient = session.get(Patient, patient_id)
            if not patient:
                raise ValueError(f"Paciente com ID {patient_id} não encontrado")
            
            # Calcular período
            period_start, period_end = ProgressReportService._calculate_period_dates(
                period_filter, start_date, end_date
            )
            
            # Buscar todas as execuções do período
            statement = select(ExerciseExecution).where(
                and_(
                    ExerciseExecution.patient_id == patient_id,
                    ExerciseExecution.execution_date >= period_start,
                    ExerciseExecution.execution_date <= period_end
                )
            ).order_by(ExerciseExecution.execution_date)
            
            executions = list(session.exec(statement).all())
            
            # Verificar se há dados
            has_data = len(executions) > 0
            
            if not has_data:
                return ProgressReportResponse(
                    patient_id=patient_id,
                    patient_name=patient.name,
                    period_start=period_start,
                    period_end=period_end,
                    generated_at=datetime.utcnow(),
                    total_days_with_exercise=0,
                    total_activity_time_minutes=0.0,
                    total_executions=0,
                    average_completion_rate=0.0,
                    average_pain_level=None,
                    has_data=False,
                    message=f"Não há histórico de exercícios para o período selecionado."
                )
            
            # Calcular métricas gerais
            total_activity_time = sum(e.duration_minutes or 0.0 for e in executions)
            total_completion_rate = sum(e.completion_rate for e in executions)
            average_completion_rate = total_completion_rate / len(executions) if executions else 0.0
            
            # Dias únicos com exercício
            unique_dates = set(e.execution_date.date() for e in executions)
            total_days_with_exercise = len(unique_dates)
            
            # Buscar níveis de dor e calcular média
            pain_levels_statement = select(PainLevel).join(
                ExerciseExecution, PainLevel.execution_id == ExerciseExecution.id
            ).where(
                and_(
                    ExerciseExecution.patient_id == patient_id,
                    ExerciseExecution.execution_date >= period_start,
                    ExerciseExecution.execution_date <= period_end
                )
            )
            
            pain_levels = list(session.exec(pain_levels_statement).all())
            average_pain_level = None
            if pain_levels:
                total_pain = sum(p.pain_level for p in pain_levels)
                average_pain_level = total_pain / len(pain_levels)
            
            # Evolução da dor (agrupar por dia)
            pain_by_date: Dict[datetime.date, List[float]] = defaultdict(list)
            executions_by_date: Dict[datetime.date, int] = defaultdict(int)
            
            for execution in executions:
                date_key = execution.execution_date.date()
                executions_by_date[date_key] += 1
                
                # Buscar níveis de dor desta execução
                exec_pain_statement = select(PainLevel).where(
                    PainLevel.execution_id == execution.id
                )
                exec_pain_levels = list(session.exec(exec_pain_statement).all())
                if exec_pain_levels:
                    avg_exec_pain = sum(p.pain_level for p in exec_pain_levels) / len(exec_pain_levels)
                    pain_by_date[date_key].append(avg_exec_pain)
            
            # Criar lista de evolução da dor
            pain_evolution = []
            for date_key in sorted(pain_by_date.keys()):
                avg_pain = sum(pain_by_date[date_key]) / len(pain_by_date[date_key])
                pain_evolution.append(PainEvolutionItem(
                    date=datetime.combine(date_key, datetime.min.time()),
                    pain_level=avg_pain,
                    execution_count=executions_by_date[date_key]
                ))
            
            # Progresso por exercício
            exercises_progress_map: Dict[int, Dict] = defaultdict(lambda: {
                'total_executions': 0,
                'total_completion_rate': 0.0,
                'unique_dates': set(),
                'last_execution_date': None,
                'exercise_id': None,
                'exercise_name': None
            })
            
            for execution in executions:
                prescription = session.get(Prescription, execution.prescription_id)
                if prescription:
                    exercise_id = prescription.exercise_id
                    exercise = session.get(ExerciseLibrary, exercise_id)
                    
                    if exercise:
                        exercises_progress_map[exercise_id]['exercise_id'] = exercise_id
                        exercises_progress_map[exercise_id]['exercise_name'] = exercise.name
                        exercises_progress_map[exercise_id]['total_executions'] += 1
                        exercises_progress_map[exercise_id]['total_completion_rate'] += execution.completion_rate
                        exercises_progress_map[exercise_id]['unique_dates'].add(execution.execution_date.date())
                        
                        if (not exercises_progress_map[exercise_id]['last_execution_date'] or 
                            execution.execution_date > exercises_progress_map[exercise_id]['last_execution_date']):
                            exercises_progress_map[exercise_id]['last_execution_date'] = execution.execution_date
            
            exercises_progress = []
            for exercise_id, data in exercises_progress_map.items():
                avg_completion = data['total_completion_rate'] / data['total_executions'] if data['total_executions'] > 0 else 0.0
                exercises_progress.append(ExerciseProgress(
                    exercise_id=data['exercise_id'],
                    exercise_name=data['exercise_name'],
                    total_executions=data['total_executions'],
                    completion_rate_avg=avg_completion,
                    days_performed=len(data['unique_dates']),
                    last_execution_date=data['last_execution_date']
                ))
            
            # Calcular metas alcançadas (simplificado - pode ser expandido)
            goals_achieved = []
            
            # Meta: fazer exercício pelo menos 3 vezes por semana
            days_in_period = (period_end - period_start).days + 1
            weeks_in_period = days_in_period / 7.0
            target_executions_per_week = 3
            target_total = target_executions_per_week * weeks_in_period
            actual_executions = len(executions)
            execution_percentage = (actual_executions / target_total * 100) if target_total > 0 else 0.0
            
            actual_executions_per_week = actual_executions / weeks_in_period if weeks_in_period > 0 else 0.0
            goals_achieved.append(GoalAchievement(
                goal_type="exercises_per_week",
                target=float(target_executions_per_week),
                achieved=actual_executions_per_week,
                percentage=min(execution_percentage, 100.0),
                is_achieved=actual_executions >= target_total
            ))
            
            return ProgressReportResponse(
                patient_id=patient_id,
                patient_name=patient.name,
                period_start=period_start,
                period_end=period_end,
                generated_at=datetime.utcnow(),
                total_days_with_exercise=total_days_with_exercise,
                total_activity_time_minutes=total_activity_time,
                total_executions=len(executions),
                average_completion_rate=average_completion_rate,
                average_pain_level=average_pain_level,
                pain_evolution=pain_evolution,
                exercises_progress=exercises_progress,
                goals_achieved=goals_achieved,
                has_data=True,
                message=None
            )
            
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Erro ao gerar relatório de progresso: {str(e)}")