from sqlmodel import Session, select
from typing import List, Optional
from app.models.prescription import Prescription
from app.models.exercise_library import ExerciseLibrary
from app.models.patient import Patient
from app.schemas.prescription import PrescriptionCreate, PrescriptionUpdate


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
        prescription_data: PrescriptionUpdate
    ) -> Optional[Prescription]:
        """Atualiza uma prescrição"""
        prescription = session.get(Prescription, prescription_id)
        if not prescription:
            return None
        
        update_data = prescription_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(prescription, field, value)
        
        session.add(prescription)
        session.commit()
        session.refresh(prescription)
        
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
