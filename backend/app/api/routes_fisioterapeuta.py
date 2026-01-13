# backend/app/api/routes_fisioterapeuta.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
from pathlib import Path

# permitir importar coisas da pasta backend
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cadastro_fisioterapeuta import cadastrar_fisioterapeuta
from repositorio_memoria import repo_fisio_memoria as repo_fisio

router = APIRouter()


class FisioterapeutaCriacao(BaseModel):
    nome: str
    cpf: str
    registro: str
    email: str
    cnpj: str | None = None
    senha: str


@router.post("/fisioterapeutas")
def criar_fisioterapeuta(dados: FisioterapeutaCriacao):
    erros = cadastrar_fisioterapeuta(dados.dict(), repo_fisio)
    if erros:
        # se houver erros de validação/duplicidade
        raise HTTPException(status_code=400, detail=erros)

    return {"mensagem": "Fisioterapeuta cadastrado com sucesso."}


@router.get("/fisioterapeutas/debug/fisios")
def listar_fisios_debug():
    """Rota só pra debug: mostra o que está em memória."""
    return repo_fisio._fisioterapeutas
