from typing import List, Optional

from sqlmodel import Session, select

from app.core.config import settings
from app.core.security import hash_password
from app.models.patient import Patient
from app.schemas.patient import PatientCreate


class PatientService:
    @staticmethod
    def create_patient(session: Session, data: PatientCreate) -> Patient:
        """Cria um paciente no banco, garantindo e-mail único."""

        # Verifica se já existe paciente com esse e-mail
        existing = session.exec(
            select(Patient).where(Patient.email == data.email)
        ).first()

        if existing:
            raise ValueError("Já existe um paciente cadastrado com esse e-mail.")

        patient = Patient(
            name=data.name,
            email=data.email,
            phone=data.phone,
            birth_date=data.birth_date,
            physiotherapist_id=data.physiotherapist_id,
            password_hash=hash_password(settings.DEFAULT_PATIENT_PASSWORD),
            must_change_password=True,
        )

        session.add(patient)
        session.commit()
        session.refresh(patient)
        return patient

    @staticmethod
    def get_patient(session: Session, patient_id: int) -> Optional[Patient]:
        return session.get(Patient, patient_id)

    @staticmethod
    def list_patients(session: Session) -> List[Patient]:
        return session.exec(select(Patient)).all()