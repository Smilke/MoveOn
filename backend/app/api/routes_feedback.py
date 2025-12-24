from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from cadastro_feedback import cadastrar_feedback
from repositorio_memoria import RepositorioFeedbackMemoria

router = APIRouter()

repo_feedback = RepositorioFeedbackMemoria()


class FeedbackIn(BaseModel):
    paciente_id: str
    fisioterapeuta_id: str
    feedback: str              # nome que o front vai mandar
    avaliacao: int | None = None
    exercicio_id: str | None = None  # opcional por enquanto


@router.post("/feedbacks", status_code=status.HTTP_201_CREATED)
def criar_feedback(body: FeedbackIn):
    """
    Registra um feedback de paciente (PB07).

    - Usa cadastrar_feedback (que já chama validar_feedback_paciente)
    - Adiciona data/hora no serviço
    - Se tiver erro, responde 400 com lista de erros
    """
    dados = body.dict()
    erros = cadastrar_feedback(dados, repo_feedback)

    if erros:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=erros,
        )

    return {"mensagem": "Feedback registrado com sucesso"}

@router.get("/pacientes/{paciente_id}/feedbacks")
def listar_feedbacks_paciente(paciente_id: str):
    """
    Lista todos os feedbacks de um paciente específico.
    Útil pro fisio ver o histórico de feedbacks.
    """
    return repo_feedback.listar_por_paciente(paciente_id)

