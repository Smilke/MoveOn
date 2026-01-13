# backend/app/api/routes_login.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
from pathlib import Path
import hashlib

# permite importar o repositorio_memoria a partir da pasta backend
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from repositorio_memoria import repo_fisio_memoria, repo_paciente_memoria

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    senha: str


def hash_senha(senha: str) -> str:
    """Gera um hash SHA-256 da senha (simples, para fins didáticos)."""
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


@router.post("/login")
def login(dados: LoginRequest):
    email = dados.email.strip()
    senha = dados.senha.strip()

    if not email or not senha:
        raise HTTPException(
            status_code=400,
            detail="E-mail e senha são obrigatórios."
        )

    senha_hash = hash_senha(senha)

    # 1) tenta encontrar como fisioterapeuta
    for f in repo_fisio_memoria._fisioterapeutas:
        if f.get("email") == email and f.get("senha_hash") == senha_hash:
            return {
                "tipo": "fisioterapeuta",
                "nome": f.get("nome"),
                "cpf": f.get("cpf"),
                "email": f.get("email"),
            }

    # 2) tenta encontrar como paciente
    for p in repo_paciente_memoria._pacientes:
        if p.get("email") == email and p.get("senha_hash") == senha_hash:
            return {
                "tipo": "paciente",
                "nome": p.get("nome"),
                "cpf": p.get("cpf"),
                "email": p.get("email"),
            }

    raise HTTPException(status_code=401, detail="Credenciais inválidas.")
