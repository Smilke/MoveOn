from sqlmodel import Session, select
from typing import List, Optional
from app.models.prescription import Prescription
from app.models.exercise_library import ExerciseLibrary
from app.models.patient import Patient
from app.schemas.prescription import PrescriptionCreate, PrescriptionUpdate
from datetime import date

class PrescriptionService:
    """Serviço para gerenciar prescrições de exercícios"""

    @staticmethod
    def create_prescription(
        session: Session,
        prescription_data: PrescriptionCreate
    ) -> Prescription:
        """Cria uma nova prescrição"""
        # Verificar se o exercício existe
        exercise = session.get(ExerciseLibrary, prescription_data.exercise_id)
        if not exercise:
            raise ValueError(f"Exercício com ID {prescription_data.exercise_id} não encontrado")
        
        if not exercise.is_active:
            raise ValueError("Exercício não está ativo")
        
        # Verificar se o paciente existe
        patient = session.get(Patient, prescription_data.patient_id)
        if not patient:
            raise ValueError(f"Paciente com ID {prescription_data.patient_id} não encontrado")
        
        # Criar prescrição
        prescription = Prescription(**prescription_data.model_dump())
        session.add(prescription)
        session.commit()
        session.refresh(prescription)
        
        return prescription

    @staticmethod
    def get_prescription(session: Session, prescription_id: int) -> Optional[Prescription]:
        """Obtém uma prescrição por ID"""
        return session.get(Prescription, prescription_id)

    @staticmethod
    def get_patient_prescriptions(
        session: Session,
        patient_id: int,
        active_only: bool = True
    ) -> List[Prescription]:
        """Obtém todas as prescrições de um paciente"""
        statement = select(Prescription).where(Prescription.patient_id == patient_id)
        
        if active_only:
            statement = statement.where(Prescription.is_active == True)
        
        return list(session.exec(statement).all())

    @staticmethod
    def get_all_exercises(session: Session, active_only: bool = True) -> List[ExerciseLibrary]:
        """Obtém todos os exercícios da biblioteca"""
        statement = select(ExerciseLibrary)
        
        if active_only:
            statement = statement.where(ExerciseLibrary.is_active == True)
        
        return list(session.exec(statement.order_by(ExerciseLibrary.name)).all())

    @staticmethod
    def update_prescription(
        session: Session,
        prescription_id: int,
        prescription_data: PrescriptionUpdate,
        physiotherapist_id: Optional[int] = None,
        change_reason: Optional[str] = None
    ) -> Optional[Prescription]:
        """Atualiza uma prescrição e registra no histórico
        
        Args:
            session: Sessão do banco de dados
            prescription_id: ID da prescrição a ser atualizada
            prescription_data: Dados para atualização
            physiotherapist_id: ID do fisioterapeuta que está fazendo a alteração
            change_reason: Motivo da alteração (ex: "Paciente relatou dor")
        
        Returns:
            Prescrição atualizada ou None se não encontrada
        """
        from app.models.prescription_history import PrescriptionHistory
        
        prescription = session.get(Prescription, prescription_id)
        if not prescription:
            return None
        
        # Capturar valores antigos antes da atualização
        old_values = {
            'repetitions': prescription.repetitions,
            'series': prescription.series,
            'duration_minutes': prescription.duration_minutes,
            'difficulty_level': prescription.difficulty_level,
            'weekly_frequency': prescription.weekly_frequency,
        }
        
        # Aplicar as mudanças
        update_data = prescription_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(prescription, field, value)
        
        session.add(prescription)
        session.commit()
        session.refresh(prescription)
        
        # Criar registro no histórico se houver mudanças nos parâmetros
        if physiotherapist_id and any(
            field in update_data 
            for field in ['repetitions', 'series', 'duration_minutes', 'difficulty_level', 'weekly_frequency']
        ):
            from app.models.physiotherapist import Physiotherapist
            
            # Garantir que o fisioterapeuta exista
            if not session.get(Physiotherapist, physiotherapist_id):
                # Se não existir, ainda retornamos a prescrição atualizada mas não salvamos histórico
                # ou poderíamos lançar um erro. Para consistência, vamos apenas logar (implícito).
                return prescription

            history_entry = PrescriptionHistory(
                prescription_id=prescription_id,
                physiotherapist_id=physiotherapist_id,
                old_repetitions=old_values.get('repetitions'),
                old_series=old_values.get('series'),
                old_duration_minutes=old_values.get('duration_minutes'),
                old_difficulty_level=old_values.get('difficulty_level'),
                old_weekly_frequency=old_values.get('weekly_frequency'),
                new_repetitions=prescription.repetitions,
                new_series=prescription.series,
                new_duration_minutes=prescription.duration_minutes,
                new_difficulty_level=prescription.difficulty_level,
                new_weekly_frequency=prescription.weekly_frequency,
                change_reason=change_reason,
            )
            session.add(history_entry)
            session.commit()
        
        return prescription

    @staticmethod
    def delete_prescription(session: Session, prescription_id: int) -> bool:
        """Desativa uma prescrição (soft delete)"""
        prescription = session.get(Prescription, prescription_id)
        if not prescription:
            return False
        
        prescription.is_active = False
        session.add(prescription)
        session.commit()
        
        return True

    @staticmethod
    def get_prescriptions_for_today(session: Session, patient_id: int) -> List[Prescription]:
        """Obtém as prescrições de exercícios de um paciente para o dia atual
        
        Retorna prescrições que:
        1. Têm scheduled_date igual a hoje (exercícios agendados especificamente)
        2. OU são prescrições ativas sem data específica (seguem o plano de weekly_frequency)
        """
        from sqlalchemy import or_
        today = date.today()
        
        statement = select(Prescription).where(
            Prescription.patient_id == patient_id,
            Prescription.is_active == True,
            or_(
                Prescription.scheduled_date == today,  # Exercícios agendados para hoje
                Prescription.scheduled_date == None    # Exercícios do plano regular (sem data específica)
            )
        )
        return list(session.exec(statement).all())

    @staticmethod
    def get_prescription_history(session: Session, prescription_id: int) -> List["PrescriptionHistory"]:
        """Obtém o histórico de alterações de uma prescrição
        
        Args:
            session: Sessão do banco de dados
            prescription_id: ID da prescrição
        
        Returns:
            Lista de registros de histórico ordenados por data (mais recente primeiro)
        """
        from app.models.prescription_history import PrescriptionHistory
        
        statement = select(PrescriptionHistory).where(
            PrescriptionHistory.prescription_id == prescription_id
        ).order_by(PrescriptionHistory.changed_at.desc())
        
        return list(session.exec(statement).all())