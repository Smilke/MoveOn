from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.prescription import Prescription
    from app.models.patient import Patient
    from app.models.pain_level import PainLevel
    from app.models.feedback import Feedback

class ExerciseExecution(SQLModel, table=True):
    """Execução de exercício pelo paciente."""
    __tablename__ = "exercise_executions"

    id: Optional[int] = Field(default=None, primary_key=True)
    prescription_id: int = Field(foreign_key="prescriptions.id")
    patient_id: int = Field(foreign_key="patients.id")

    # Dados da execução
    execution_date: datetime = Field(default_factory=datetime.utcnow, index=True)
    repetitions_completed: Optional[int] = Field(default=None, ge=0)
    series_completed: Optional[int] = Field(default=None, ge=0)
    duration_minutes: Optional[float] = Field(default=None, ge=0)
    completion_rate: float = Field(default=0.0, ge=0.0, le=100.0)  # Taxa de conclusão em %
    was_completed: bool = Field(default=False)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    # updated_at removido para compatibilidade com esquema antigo/revertido se necessario, 
    # mas ideal é ter. Como o erro foi falta de coluna, e user quer fix...
    # Vou manter SEM updated_at para evitar o erro de coluna faltando se o DB não tiver migrado.

    # Relacionamentos
    prescription: "Prescription" = Relationship(back_populates="executions")
    patient: "Patient" = Relationship(back_populates="exercise_executions")
    pain_levels: List["PainLevel"] = Relationship(back_populates="execution")
    feedbacks: List["Feedback"] = Relationship(back_populates="execution")
