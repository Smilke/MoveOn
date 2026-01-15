from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.exercise_execution import ExerciseExecution

class Feedback(SQLModel, table=True):
    __tablename__ = "feedbacks"

    id: Optional[int] = Field(default=None, primary_key=True)
    execution_id: int = Field(foreign_key="exercise_executions.id")
    patient_id: int = Field(foreign_key="patients.id")
    
    feedback_type: str  # 'positive', 'negative', 'neutral'
    content: str
    is_positive: bool = True
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relacionamentos
    execution: "ExerciseExecution" = Relationship(back_populates="feedbacks")
