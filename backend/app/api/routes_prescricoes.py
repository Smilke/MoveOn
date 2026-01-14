# backend/app/api/routes_prescricoes.py

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
import sys
from pathlib import Path

# permitir importar coisas da raiz do backend
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from prescrever_exercicio import prescrever_exercicio
from repositorio_prescricao_memoria import (
    repo_exercicio_memoria,
    repo_prescricao_memoria,
)

router = APIRouter()


class PrescricaoIn(BaseModel):
    """
    Corpo da requisição para prescrever exercício.

    O paciente_id vem na URL, aqui vão os parâmetros do exercício.
    """

    exercicio_id: int = Field(..., description="ID do exercício na biblioteca")
    series: int = Field(..., gt=0, description="Número de séries")
    repeticoes: int = Field(..., gt=0, description="Número de repetições")
    duracao_minutos: Optional[int] = Field(
        default=None, gt=0, description="Duração em minutos (opcional)"
    )
    frequencia_semanal: int = Field(..., gt=0, description="Vezes por semana")
    nivel_dificuldade: Optional[str] = Field(
        default=None, description="Nível de dificuldade (opcional)"
    )


class PrescricaoOut(BaseModel):
    id: Optional[int]
    paciente_id: str
    exercicio_id: int
    nome_exercicio: Optional[str]
    series: int
    repeticoes: int
    duracao_minutos: Optional[int]
    frequencia_semanal: int
    nivel_dificuldade: Optional[str]


@router.post(
    "/pacientes/{paciente_id}/prescricoes",
    status_code=status.HTTP_201_CREATED,
)
def criar_prescricao(paciente_id: str, body: PrescricaoIn):
    """
    Prescreve um exercício gamificado para um paciente (PB03).
    """

    dados = {
        "paciente_id": paciente_id,
        "exercicio_id": body.exercicio_id,
        "series": body.series,
        "repeticoes": body.repeticoes,
        "duracao_minutos": body.duracao_minutos,
        "frequencia_semanal": body.frequencia_semanal,
        "nivel_dificuldade": body.nivel_dificuldade,
    }

    erros, mensagem = prescrever_exercicio(
        dados,
        repo_exercicio_memoria,
        repo_prescricao_memoria,
    )

    if erros:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=erros,
        )

    return {"mensagem": mensagem or "Exercício prescrito com sucesso"}


@router.get(
    "/pacientes/{paciente_id}/prescricoes",
    response_model=List[PrescricaoOut],
)
def listar_prescricoes_paciente(paciente_id: str):
    """
    Lista todas as prescrições do paciente.
    """
    prescricoes = repo_prescricao_memoria.listar_por_paciente(paciente_id)
    return prescricoes