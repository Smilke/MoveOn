from typing import Optional, List

from sqlmodel import Session, select

from app.core.config import settings
from app.core.security import hash_password
from app.models.physiotherapist import Physiotherapist
from app.schemas.physiotherapist import PhysiotherapistCreate


class PhysiotherapistService:
    @staticmethod
    def create_physiotherapist(
        session: Session,
        data: PhysiotherapistCreate,
    ) -> Physiotherapist:
        """
        Cria um fisioterapeuta no banco garantindo CPF e e-mail únicos.
        """

        # verifica se já existe CPF ou e-mail igual
        existing = session.exec(
            select(Physiotherapist).where(
                (Physiotherapist.cpf == data.cpf)
                | (Physiotherapist.email == data.email)
            )
        ).first()

        if existing:
            raise ValueError("Já existe fisioterapeuta com esse CPF ou e-mail.")

        physio = Physiotherapist(
            name=data.name,
            cpf=data.cpf,
            email=data.email,
            license_number=data.license_number,
            password_hash=hash_password(settings.DEFAULT_PHYSIO_PASSWORD),
            must_change_password=False,
        )

        session.add(physio)
        session.commit()
        session.refresh(physio)
        return physio

    @staticmethod
    def get_by_id(session: Session, physio_id: int) -> Optional[Physiotherapist]:
        return session.get(Physiotherapist, physio_id)

    @staticmethod
    def get_by_cpf(session: Session, cpf: str) -> Optional[Physiotherapist]:
        return session.exec(
            select(Physiotherapist).where(Physiotherapist.cpf == cpf)
        ).first()

    @staticmethod
    def list_all(session: Session) -> List[Physiotherapist]:
        return session.exec(select(Physiotherapist)).all()