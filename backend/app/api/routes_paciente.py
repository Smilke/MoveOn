from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from cadastrar_paciente import cadastrar_paciente


router = APIRouter()


# Repositório em memória só pra API (depois pode virar banco)
class RepositorioPacienteMemoria:
    def __init__(self):
        self._pacientes = []

    def existe_paciente(self, cpf: str, fisioterapeuta_id: str) -> bool:
        return any(
            p["cpf"] == cpf and p["fisioterapeuta_id"] == fisioterapeuta_id
            for p in self._pacientes
        )

    def salvar(self, dados: dict) -> None:
        self._pacientes.append(dados)


repo_paciente = RepositorioPacienteMemoria()


class PacienteIn(BaseModel):
    nome: str
    cpf: str
    idade: int
    situacao: str | None = "em tratamento"
    fisioterapeuta_id: str   # aqui vem o ID/CPF do fisio que cadastrou


@router.post("/pacientes", status_code=status.HTTP_201_CREATED)
def criar_paciente(body: PacienteIn):
    """
    Rota de cadastro de paciente (PB02).
    Caminho final: {API_PREFIX}/pacientes

    - Vincula o paciente ao fisioterapeuta_id recebido
    """
    dados = {
        "nome": body.nome,
        "cpf": body.cpf,
        "idade": body.idade,
        "situacao": body.situacao or "em tratamento",
    }

    erros = cadastrar_paciente(dados, body.fisioterapeuta_id, repo_paciente)

    if erros:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=erros,
        )

    return {"mensagem": "Paciente cadastrado com sucesso"}
