"""Configurações do SiteBio carregadas do ambiente (.env)."""
import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy.pool import NullPool

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)

# --- Variáveis do banco (definidas ANTES da classe Config) ---
CURRENT_DATABASE = (os.getenv("CURRENT_DATABASE") or "mysql").strip().lower()
DB_USERNAME = (os.getenv("DB_USERNAME") or "").strip()
DB_PASSWORD = os.getenv("DB_PASSWORD") or ""
DB_HOST = (os.getenv("DB_HOST") or "").strip()
DB_PORT = (os.getenv("DB_PORT") or "").strip()
DB_NAME = (os.getenv("DB_NAME") or "").strip()
SQLITE_DATABASE_PATH = str(BASE_DIR / "sitebio.db")

# Padrão antigo (MySQL local), usado quando não há DB_HOST no .env
MYSQL_LOCAL_URL = "mysql+pymysql://root:@localhost/sitebio"

if CURRENT_DATABASE == "postgresql":
    _faltando = [
        nome
        for nome, valor in {
            "DB_USERNAME": DB_USERNAME,
            "DB_PASSWORD": DB_PASSWORD,
            "DB_HOST": DB_HOST,
            "DB_PORT": DB_PORT,
            "DB_NAME": DB_NAME,
        }.items()
        if not valor
    ]
    if _faltando:
        raise RuntimeError(
            "CURRENT_DATABASE=postgresql, mas faltam variáveis: " + ", ".join(_faltando)
        )


class Config:
    SECRET_KEY = (
        os.getenv("SITEBIO_SECRET_KEY")
        or os.getenv("SECRET_KEY")
        or "troque-esta-chave-em-desenvolvimento"
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

    # --- Banco de dados ---
    if CURRENT_DATABASE == "sqlite":
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{SQLITE_DATABASE_PATH}"
    elif CURRENT_DATABASE == "mysql":
        if DB_HOST:
            SQLALCHEMY_DATABASE_URI = (
                f"mysql+pymysql://{DB_USERNAME}:{quote_plus(DB_PASSWORD)}"
                f"@{DB_HOST}:{DB_PORT or 3306}/{DB_NAME}"
            )
        else:
            SQLALCHEMY_DATABASE_URI = os.getenv("SITEBIO_DATABASE_URL", MYSQL_LOCAL_URL)
    elif CURRENT_DATABASE == "postgresql":
        SQLALCHEMY_DATABASE_URI = (
            f"postgresql+psycopg2://{DB_USERNAME}:{quote_plus(DB_PASSWORD)}"
            f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
        # Recomendado com o Transaction pooler do Supabase (serverless)
        SQLALCHEMY_ENGINE_OPTIONS = {"poolclass": NullPool}
    else:
        raise RuntimeError(
            f"CURRENT_DATABASE inválido: '{CURRENT_DATABASE}'. Use sqlite, mysql ou postgresql."
        )
