from __future__ import annotations

import smtplib
from email.message import EmailMessage

from app.core.config import settings


def smtp_is_configured() -> bool:
    return bool(settings.SMTP_HOST and settings.SMTP_FROM)


def send_password_reset_email(to_email: str, token: str) -> None:
    if not smtp_is_configured():
        raise RuntimeError("SMTP não configurado (defina SMTP_HOST e SMTP_FROM)")

    msg = EmailMessage()
    msg["Subject"] = "MoveOn - Recuperação de senha"
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email

    body = (
        "Você solicitou a recuperação de senha no MoveOn.\n\n"
        f"Seu token de recuperação é:\n\n{token}\n\n"
        "Se você não solicitou isso, ignore este e-mail.\n"
    )
    msg.set_content(body)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
        if settings.SMTP_USE_TLS:
            server.starttls()
        if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(msg)
