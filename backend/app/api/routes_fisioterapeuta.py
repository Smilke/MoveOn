from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cadastro_fisioterapeuta import cadastrar_fisioterapeuta
from repositorio_memoria import repo_fisio_memoria  # INSTÂNCIA COMPARTILHADA

router = APIRouter()


class FisioterapeutaIn(BaseModel):
    nome: str
    cpf: str
    registro: str
    email: EmailStr
    cnpj: str | None = ""
    senha: str | None = None   # 🌟 campo novo


@router.post("/fisioterapeutas", status_code=status.HTTP_201_CREATED)
def criar_fisioterapeuta(body: FisioterapeutaIn):
    dados = {
        "nome": body.nome,
        "cpf": body.cpf,
        "registro": body.registro,
        "email": body.email,
        "cnpj": body.cnpj or "",
    }

    # se vier senha no body, passa pra função de cadastro
    if body.senha:
        dados["senha"] = body.senha

    erros = cadastrar_fisioterapeuta(dados, repo_fisio_memoria)

    if erros:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=erros,
        )

    return {"mensagem": "Fisioterapeuta cadastrado com sucesso."}
