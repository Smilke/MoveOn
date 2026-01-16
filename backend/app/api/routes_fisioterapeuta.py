from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from sqlmodel import Session
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.core.database import get_session
from app.core.security import hash_password
from app.models.physiotherapist import Physiotherapist
from repositorio_memoria import repo_fisio_memoria  # Mantido para compatibilidade se necessário

router = APIRouter()


class FisioterapeutaIn(BaseModel):
    nome: str
    cpf: str
    registro: str
    email: EmailStr
    cnpj: str | None = ""
    senha: str | None = None


@router.post("/fisioterapeutas", status_code=status.HTTP_201_CREATED)
def criar_fisioterapeuta(body: FisioterapeutaIn, session: Session = Depends(get_session)):
    # Verifica se já existe por email ou cpf ou registro
    from sqlmodel import select
    existente = session.exec(
        select(Physiotherapist).where(
            (Physiotherapist.email == body.email) | 
            (Physiotherapist.cpf == body.cpf) | 
            (Physiotherapist.license_number == body.registro)
        )
    ).first()
    
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fisioterapeuta com este E-mail, CPF ou Registro já cadastrado.",
        )

    # Cria novo fisioterapeuta no banco
    novo_fisio = Physiotherapist(
        name=body.nome,
        cpf=body.cpf,
        email=body.email,
        license_number=body.registro,
        password_hash=hash_password(body.senha) if body.senha else None
    )

    try:
        session.add(novo_fisio)
        session.commit()
        session.refresh(novo_fisio)
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar no banco de dados: {str(e)}",
        )

    return {"mensagem": "Fisioterapeuta cadastrado com sucesso.", "id": novo_fisio.id}
