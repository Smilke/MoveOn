from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import sys
from pathlib import Path

# permite importar módulos da pasta backend
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cadastrar_paciente import cadastrar_paciente
from repositorio_memoria import repo_paciente_memoria, repo_fisio_memoria

router = APIRouter()


class PacienteIn(BaseModel):
    nome: str
    cpf: str
    idade: int
    situacao: str | None = "em tratamento"
    fisioterapeuta_id: str   
    email: str
    senha: str


@router.post("/pacientes", status_code=status.HTTP_201_CREATED)
def criar_paciente(body: PacienteIn):
    """
    Cadastro de paciente (PB02) já vinculado a um fisioterapeuta.
    Agora também valida se o CPF do fisioterapeuta existe.
    """

    # 1) Verificar se o fisioterapeuta existe
    if not repo_fisio_memoria.existe_cpf(body.fisioterapeuta_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=["Fisioterapeuta não encontrado para esse CPF."],
        )

    # 2) Montar os dados do paciente (sem fisioterapeuta_id ainda)
    dados = {
        "nome": body.nome,
        "cpf": body.cpf,
        "idade": body.idade,
        "situacao": body.situacao or "em tratamento",
        "email": body.email,
        "senha": body.senha,
    }

    # 3) Chamar a função de cadastro de paciente
    erros = cadastrar_paciente(dados, body.fisioterapeuta_id, repo_paciente_memoria)

    if erros:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=erros,
        )

    return {"mensagem": "Paciente cadastrado com sucesso."}

@router.get("/fisioterapeutas/{fisioterapeuta_id}/pacientes")
def listar_pacientes_do_fisio(fisioterapeuta_id: str):
    """
    Retorna todos os pacientes vinculados ao fisioterapeuta informado (CPF).
    Usado na Área do Fisioterapeuta no HTML.
    """
    pacientes_do_fisio = [
        {
            "nome": p.get("nome"),
            "cpf": p.get("cpf"),
            "idade": p.get("idade"),
            "situacao": p.get("situacao"),
        }
        for p in repo_paciente_memoria._pacientes
        if p.get("fisioterapeuta_id") == fisioterapeuta_id
    ]

    return pacientes_do_fisio
