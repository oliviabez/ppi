"""Configurações do SiteBio carregadas do ambiente (.env)."""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.getenv("SITEBIO_SECRET_KEY", "troque-esta-chave-em-desenvolvimento")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SITEBIO_DATABASE_URL",
        "mysql+pymysql://root:@localhost/sitebio"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Código de CONVITE para criar contas de administrador. Sem valor padrão: se estiver vazio,
    # o cadastro de administradores fica desativado (defina SITEBIO_ADMIN_CODIGO no .env).
    ADMIN_CODIGO = os.getenv("SITEBIO_ADMIN_CODIGO", "").strip()
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SITEBIO_COOKIE_SECURE", "0") == "1"
    SMTP_HOST = os.getenv("SITEBIO_SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SITEBIO_SMTP_PORT", "587"))
    SMTP_USUARIO = os.getenv("SITEBIO_SMTP_USUARIO", "")
    SMTP_SENHA = os.getenv("SITEBIO_SMTP_SENHA", "")
    EMAIL_REMETENTE = os.getenv("SITEBIO_EMAIL_REMETENTE", "") or SMTP_USUARIO
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
