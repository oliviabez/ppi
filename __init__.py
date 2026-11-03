import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# ─── CONFIGURAÇÃO ──────────────────────────────────────────────────────────────
# ATENÇÃO: a chave abaixo é a de DESENVOLVIMENTO. Quem tem a chave consegue forjar o
# cookie de sessão (ou seja, "virar" qualquer usuário, inclusive admin).
# Em produção defina a variável de ambiente SITEBIO_SECRET_KEY com um valor longo e aleatório.
app.secret_key = os.environ.get('SITEBIO_SECRET_KEY', 'sitebio_secret_key_dev')

# Cookie de sessão: não acessível por JavaScript e não enviado em requisições de outros sites.
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
# ATENÇÃO: ao publicar com HTTPS, ligue também:  app.config['SESSION_COOKIE_SECURE'] = True

# ─── BANCO DE DADOS ────────────────────────────────────────────────────────────
# SITEBIO_USAR_BANCO=0 (padrão) -> funciona 100% em MEMÓRIA, sem banco. Dá para testar tudo.
#                                  LIMITAÇÃO: os dados somem quando o servidor reinicia.
# SITEBIO_USAR_BANCO=1          -> usa o banco de SITEBIO_DATABASE_URL (as tabelas são criadas
#                                  automaticamente com db.create_all()).
# TODO(BANCO): quando baixar o banco, é só trocar a URL abaixo (ou a variável de ambiente), ex.:
#     MySQL:      mysql+pymysql://usuario:senha@localhost/sitebio      (pip install pymysql)
#     PostgreSQL: postgresql+psycopg2://usuario:senha@localhost/sitebio (pip install psycopg2-binary)
app.config['USAR_BANCO'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Oi_olivk961@localhost/sitebio'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Código exigido para criar conta com perfil "Administrador".
# ATENÇÃO: sem isso qualquer visitante poderia se cadastrar como admin. Troque o valor padrão!
app.config['ADMIN_CODIGO'] = os.environ.get('SITEBIO_ADMIN_CODIGO', 'sitebio-admin')

# ─── E-MAIL (recuperar senha, confirmar cadastro, avisos de resposta) ────────────
# Sem SITEBIO_SMTP_HOST o e-mail é só impresso no terminal (modo desenvolvimento).
# Exemplo Gmail: host smtp.gmail.com, porta 587, usuário = seu gmail, senha = "senha de app".
app.config['SMTP_HOST'] = os.environ.get('SITEBIO_SMTP_HOST', '')
app.config['SMTP_PORT'] = int(os.environ.get('SITEBIO_SMTP_PORT', '587'))
app.config['SMTP_USUARIO'] = os.environ.get('SITEBIO_SMTP_USUARIO', '')
app.config['SMTP_SENHA'] = os.environ.get('SITEBIO_SMTP_SENHA', '')
app.config['EMAIL_REMETENTE'] = os.environ.get('SITEBIO_EMAIL_REMETENTE', '') or app.config['SMTP_USUARIO']

# ─── UPLOAD DE IMAGENS DOS CONTEÚDOS ──────────────────────────────────────────
app.config['PASTA_UPLOADS'] = os.path.join(app.root_path, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024      # limite total por envio (16 MB)
os.makedirs(app.config['PASTA_UPLOADS'], exist_ok=True)

db = SQLAlchemy(app)

from app import models  # noqa: E402,F401  (registra as tabelas no SQLAlchemy)
from app import routes  # noqa: E402,F401

if app.config['USAR_BANCO']:
    with app.app_context():
        db.create_all()
else:
    # Modo memória: cria contas e um conteúdo de exemplo para você ver o sistema funcionando.
    from app.services import memoria
    memoria.semear_demo()
