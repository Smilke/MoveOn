from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select

from app.core.config import settings
from app.core.database import get_session
from app.core.emailer import send_password_reset_email, smtp_is_configured
from app.core.security import (
    generate_reset_token,
    hash_password,
    hash_reset_token,
)
from app.models.patient import Patient
from app.models.physiotherapist import Physiotherapist

router = APIRouter()


class EsqueciSenhaIn(BaseModel):
    email: EmailStr


@router.post("/esqueci-senha")
def esqueci_senha(body: EsqueciSenhaIn, session: Session = Depends(get_session)):
    """
    PB14 - Início do fluxo de recuperação de senha.
    Recebe um e-mail, tenta localizar usuário (fisio ou paciente)
    e gera um token de redefinição.
    """
    email = body.email.strip().lower()

    # find user (patient or physio)
    user_type = None
    user = session.exec(select(Patient).where(Patient.email == email)).first()
    if user:
        user_type = "patient"
    else:
        user = session.exec(select(Physiotherapist).where(Physiotherapist.email == email)).first()
        if user:
            user_type = "physio"

    # Always return generic success (avoid leaking whether email exists)
    if not user:
        return {
            "mensagem": "Se o e-mail existir no sistema, enviaremos um token de recuperação.",
        }

    token = generate_reset_token()
    token_hash = hash_reset_token(token)
    expires_at = datetime.utcnow() + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_MINUTES)

    user.password_reset_token_hash = token_hash
    user.password_reset_expires_at = expires_at
    session.add(user)
    session.commit()

    # send email (or fallback)
    if smtp_is_configured():
        try:
            send_password_reset_email(email, token)
            return {
                "mensagem": "Token enviado para o e-mail cadastrado.",
            }
        except Exception as e:
            if not settings.EMAIL_FALLBACK_RETURN_TOKEN:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Falha ao enviar e-mail: {str(e)}",
                )

    # fallback (dev)
    if settings.EMAIL_FALLBACK_RETURN_TOKEN:
        return {
            "mensagem": "Token gerado. SMTP não configurado; token retornado na resposta para ambiente de desenvolvimento.",
            "token": token,
            "expires_at": expires_at.isoformat() + "Z",
            "user_type": user_type,
        }

    return {"mensagem": "Token gerado."}


class RedefinirSenhaIn(BaseModel):
    token: str
    nova_senha: str


@router.post("/redefinir-senha")
def redefinir_senha(body: RedefinirSenhaIn, session: Session = Depends(get_session)):
    """
    PB14 - Conclusão do fluxo de recuperação de senha.
    Recebe token + nova senha e efetiva a troca.
    """
    if not body.token or not body.nova_senha:
        raise HTTPException(status_code=400, detail="Token e nova senha são obrigatórios.")
    if len(body.nova_senha) < 8:
        raise HTTPException(status_code=400, detail="A nova senha deve ter no mínimo 8 caracteres.")

    token_hash = hash_reset_token(body.token.strip())
    now = datetime.utcnow()

    patient = session.exec(select(Patient).where(Patient.password_reset_token_hash == token_hash)).first()
    physio = None
    user = patient
    if not user:
        physio = session.exec(
            select(Physiotherapist).where(Physiotherapist.password_reset_token_hash == token_hash)
        ).first()
        user = physio

    if not user:
        raise HTTPException(status_code=400, detail="Token inválido.")
    if not user.password_reset_expires_at or user.password_reset_expires_at < now:
        raise HTTPException(status_code=400, detail="Token expirado. Solicite um novo token.")

    user.password_hash = hash_password(body.nova_senha)
    user.must_change_password = False
    user.password_reset_token_hash = None
    user.password_reset_expires_at = None
    session.add(user)
    session.commit()

    return {"mensagem": "Senha redefinida com sucesso."}


class TrocarSenhaIn(BaseModel):
    senha_atual: str
    nova_senha: str


@router.post("/patients/{patient_id}/trocar-senha")
def trocar_senha_primeiro_login(
    patient_id: int,
    body: TrocarSenhaIn,
    session: Session = Depends(get_session),
):
    if not body.senha_atual or not body.nova_senha:
        raise HTTPException(status_code=400, detail="Informe a senha atual e a nova senha.")
    if len(body.nova_senha) < 8:
        raise HTTPException(status_code=400, detail="A nova senha deve ter no mínimo 8 caracteres.")

    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    if not patient.password_hash:
        patient.password_hash = hash_password(settings.DEFAULT_PATIENT_PASSWORD)
        patient.must_change_password = True

    from app.core.security import verify_password

    if not verify_password(body.senha_atual, patient.password_hash):
        raise HTTPException(status_code=401, detail="Senha atual inválida")

    patient.password_hash = hash_password(body.nova_senha)
    patient.must_change_password = False
    session.add(patient)
    session.commit()

    return {"mensagem": "Senha atualizada com sucesso."}
