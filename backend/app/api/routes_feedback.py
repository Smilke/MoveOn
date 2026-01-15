from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

import sys
from pathlib import Path

# permite importar módulos da pasta backend (nível acima de app/)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from validacao_feedback import validar_feedback_paciente
from repositorio_memoria import repo_feedback_memoria

router = APIRouter()


class FeedbackIn(BaseModel):
    paciente_id: str
    fisioterapeuta_id: str
    mensagem: str
    avaliacao: int | None = None


@router.post("/feedbacks", status_code=status.HTTP_201_CREATED)
def criar_feedback(body: FeedbackIn):
    """
    PB07 - Registro de feedback do paciente.

    Endpoint: POST /api/feedbacks
    Body esperado (JSON):
    {
      "paciente_id": "12345678901",
      "fisioterapeuta_id": "11122233344",
      "mensagem": "O atendimento foi excelente.",
      "avaliacao": 5
    }
    """
    dados = body.dict()

    # usa a função de validação que você já fez nos testes
    erros = validar_feedback_paciente(dados)
    if erros:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=erros,
        )

    salvo = repo_feedback_memoria.salvar(dados)

    return {
        "mensagem": "Feedback registrado com sucesso.",
        "id": salvo["id"],
    }

@router.get("/fisioterapeutas/{fisioterapeuta_id}/feedbacks")
def listar_feedbacks_fisio(fisioterapeuta_id: str, paciente_id: str | None = None):
    """
    Lista feedbacks recebidos por um fisioterapeuta.
    Opcionalmente filtra por paciente_id (query param).
    Ex:
      GET /api/fisioterapeutas/11122233344/feedbacks
      GET /api/fisioterapeutas/11122233344/feedbacks?paciente_id=12345678901
    """
    feedbacks = repo_feedback_memoria.listar_por_fisioterapeuta(fisioterapeuta_id)

    if paciente_id:
        feedbacks = [
            f for f in feedbacks
            if f.get("paciente_id") == paciente_id
        ]

    return feedbacks
