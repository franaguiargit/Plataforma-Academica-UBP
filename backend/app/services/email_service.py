from pathlib import Path
import logging

UPLOADS_DIR = Path(__file__).resolve().parents[2] / "uploads"
LOG_FILE = UPLOADS_DIR / "email_logs.txt"

def send_verification_email(email: str, token: str, user_id: int) -> str:
    """
    Mock: escribe el link de verificación en uploads/email_logs.txt y en logs.
    Retorna el link (para desarrollo).
    """
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    link = f"http://127.0.0.1:8000/auth/verify?token={token}"
    line = f"user_id={user_id} email={email} verify_link={link}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)
    logging.info("Sent verification link: %s", link)
    return link

def send_password_reset_email(email: str, token: str, user_id: int) -> str:
    """
    Mock: escribe link de reset en uploads/email_logs.txt y retorna el link.
    """
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    link = f"http://127.0.0.1:8000/auth/reset-password?token={token}"
    line = f"user_id={user_id} email={email} reset_link={link}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)
    logging.info("Sent password reset link: %s", link)
    return link