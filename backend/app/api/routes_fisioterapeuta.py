from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from cadastro_fisioterapeuta import cadastrar_fisioterapeuta
from repositorio_memoria import RepositorioFisioMemoria

router = APIRouter()

# repositório em memória (enquanto não tem banco)
repo_fisio = RepositorioFisioMemoria()


class FisioterapeutaIn(BaseModel):
    nome: str
    cpf: str
    registro: str
    email: str
    cnpj: str | None = ""


@router.post("/fisioterapeutas", status_code=status.HTTP_201_CREATED)
def criar_fisioterapeuta(body: FisioterapeutaIn):
    """
    Rota de cadastro de fisioterapeuta (PB01).
    Caminho final: {API_PREFIX}/fisioterapeutas
    """
    dados = body.dict()

    erros = cadastrar_fisioterapeuta(dados, repo_fisio)

    if erros:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=erros,
        )

    return {"mensagem": "Fisioterapeuta cadastrado com sucesso"}
