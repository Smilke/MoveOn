from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.core.database import get_session
from app.models.patient import Patient
from app.models.exercise_execution import ExerciseExecution
from app.models.feedback import Feedback
from app.schemas.report import FeedbackDetail

router = APIRouter()


class ExecutionFeedbackCreate(BaseModel):
    feedback_type: str = Field(..., description="Tipo do feedback: positive|neutral|negative")
    content: str = Field(..., min_length=1, description="Texto do feedback")
    is_positive: bool | None = Field(None, description="Opcional. Se não enviado, será inferido pelo feedback_type")


def _infer_is_positive(feedback_type: str) -> bool:
    ft = (feedback_type or "").strip().lower()
    if ft == "negative":
        return False
    if ft == "neutral":
        return True
    if ft == "positive":
        return True
    return True


@router.post(
    "/physiotherapists/{physio_id}/patients/{patient_id}/executions/{execution_id}/feedbacks",
    response_model=FeedbackDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Fisioterapeuta adiciona feedback em uma execução",
)
def create_execution_feedback(
    physio_id: int,
    patient_id: int,
    execution_id: int,
    body: ExecutionFeedbackCreate,
    session: Session = Depends(get_session),
):
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente não encontrado")

    if patient.physiotherapist_id != physio_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem acesso a este paciente")

    execution = session.get(ExerciseExecution, execution_id)
    if not execution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Execução não encontrada")

    if execution.patient_id != patient_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Execução não pertence ao paciente")

    feedback_type = (body.feedback_type or "").strip().lower()
    if feedback_type not in {"positive", "neutral", "negative"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="feedback_type deve ser: positive, neutral ou negative",
        )

    is_positive = body.is_positive if body.is_positive is not None else _infer_is_positive(feedback_type)

    feedback = Feedback(
        execution_id=execution_id,
        patient_id=patient_id,
        feedback_type=feedback_type,
        content=body.content.strip(),
        is_positive=is_positive,
    )

    session.add(feedback)
    session.commit()
    session.refresh(feedback)

    return FeedbackDetail(
        id=feedback.id,
        feedback_type=feedback.feedback_type,
        content=feedback.content,
        is_positive=feedback.is_positive,
        created_at=feedback.created_at,
    )
