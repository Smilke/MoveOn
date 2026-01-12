from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from repositorio_memoria import RepositorioNotificacaoMemoria
from notificacoes import (
    registrar_notificacao,
    listar_notificacoes_paciente,
)

router = APIRouter()

repo_notificacoes = RepositorioNotificacaoMemoria()


class NotificacaoIn(BaseModel):
    paciente_id: str
    tipo: str
    mensagem: str


@router.post("/notificacoes", status_code=status.HTTP_201_CREATED)
def criar_notificacao(body: NotificacaoIn):
    """
    Cria uma notificação para um paciente.
    (Por enquanto usado pra testar via Swagger/Thunder)
    """
    registrar_notificacao(
        repo_notificacoes,
        paciente_id=body.paciente_id,
        tipo=body.tipo,
        mensagem=body.mensagem,
    )

    return {"mensagem": "Notificação criada com sucesso."}


@router.get("/pacientes/{paciente_id}/notificacoes")
def listar_notificacoes(paciente_id: str):
    """
    Lista notificações de um paciente, da mais recente para a mais antiga.
    """
    notificacoes = listar_notificacoes_paciente(repo_notificacoes, paciente_id)
    return notificacoes
