from __future__ import annotations

import hashlib
import secrets
from passlib.context import CryptContext


# Use pbkdf2_sha256 to avoid bcrypt backend issues (and bcrypt's 72-byte limit).
# This is pure-python and stable across environments.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


MAX_PASSWORD_CHARS = 256


def hash_password(password: str) -> str:
    if password is None:
        raise ValueError("Senha não pode ser vazia")
    if len(password) > MAX_PASSWORD_CHARS:
        raise ValueError(
            f"Senha muito longa ({len(password)} chars). Máximo permitido: {MAX_PASSWORD_CHARS}."
        )
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        if password is None or len(password) > MAX_PASSWORD_CHARS:
            return False
        return pwd_context.verify(password, password_hash)
    except Exception:
        return False


def generate_reset_token() -> str:
    # URL-safe, ~43 chars
    return secrets.token_urlsafe(32)


def hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
import hashlib

def hash_senha(senha: str) -> str:
    """
    Gera um hash SHA-256 da senha.
    Simples, só pra não guardar senha em texto puro.
    """
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

def verificar_senha(senha_pura: str, senha_hash: str) -> bool:
    """
    Verifica se a senha pura corresponde ao hash.
    """
    return hash_senha(senha_pura) == senha_hash
