from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
from pathlib import Path

# permite importar módulos da pasta backend
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from repositorio_memoria import repo_fisio_memoria, repo_paciente_memoria
from recuperacao_senha import (
    repo_tokens_recuperacao,
    solicitar_recuperacao_senha,
    redefinir_senha as redefinir_senha_core,
)

router = APIRouter()


class EsqueciSenhaIn(BaseModel):
    email: str


@router.post("/esqueci-senha")
def esqueci_senha(body: EsqueciSenhaIn):
    """
    PB14 - Início do fluxo de recuperação de senha.
    Recebe um e-mail, tenta localizar usuário (fisio ou paciente)
    e gera um token de redefinição.
    """
    erros, token = solicitar_recuperacao_senha(
        body.email,
        repo_fisio_memoria,
        repo_paciente_memoria,
        repo_tokens_recuperacao,
    )

    if erros:
        # aqui estamos retornando 400 se o email não existe;
        # se quiser pode mudar para 200 com mensagem genérica.
        raise HTTPException(status_code=400, detail=erros)

    # como não temos envio de e-mail, devolvemos o token na resposta
    return {
        "mensagem": "Token de recuperação gerado com sucesso.",
        "token": token,
    }


class RedefinirSenhaIn(BaseModel):
    token: str
    nova_senha: str


@router.post("/redefinir-senha")
def redefinir_senha(body: RedefinirSenhaIn):
    """
    PB14 - Conclusão do fluxo de recuperação de senha.
    Recebe token + nova senha e efetiva a troca.
    """
    erros = redefinir_senha_core(
        body.token,
        body.nova_senha,
        repo_fisio_memoria,
        repo_paciente_memoria,
        repo_tokens_recuperacao,
    )

    if erros:
        raise HTTPException(status_code=400, detail=erros)

    return {"mensagem": "Senha redefinida com sucesso."}
