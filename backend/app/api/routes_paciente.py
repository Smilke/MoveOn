from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import sys
from pathlib import Path

# permite importar arquivos da pasta backend
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cadastrar_paciente import cadastrar_paciente
from repositorio_memoria import repo_paciente_memoria as repo_paciente


router = APIRouter()


class PacienteIn(BaseModel):
    nome: str
    cpf: str
    idade: int
    situacao: str | None = "em tratamento"
    fisioterapeuta_id: str       # ID/CPF do fisio que cadastrou
    email: str                   # 🔹 necessário pro login do paciente
    senha: str                   # 🔹 será transformada em senha_hash


@router.post("/pacientes", status_code=status.HTTP_201_CREATED)
def criar_paciente(body: PacienteIn):
    """
    Rota de cadastro de paciente (PB02).

    Caminho final: {API_PREFIX}/pacientes

    - Vincula o paciente ao fisioterapeuta_id recebido
    - Gera hash da senha (em cadastrar_paciente)
    - Usa repo_paciente_memoria, o mesmo que o login enxerga
    """

    # monta o dicionário que será validado e salvo
    dados = {
        "nome": body.nome,
        "cpf": body.cpf,
        "idade": body.idade,
        "situacao": body.situacao or "em tratamento",
        "email": body.email,
        "senha": body.senha,
    }

    erros = cadastrar_paciente(dados, body.fisioterapeuta_id, repo_paciente)

    if erros:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=erros,
        )

    return {"mensagem": "Paciente cadastrado com sucesso"}
