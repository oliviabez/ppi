from datetime import datetime
from app import db


class VerificacaoEmail(db.Model):
    """Códigos enviados por e-mail: confirmar o cadastro (tipo 'cadastro') e redefinir a senha
    esquecida (tipo 'senha').

    ATENÇÃO: o código NUNCA é guardado puro, só o hash.
    No tipo 'cadastro', os dados do futuro usuário ficam aqui (senha já em hash) até o e-mail
    ser confirmado; só então a conta é criada.
    """
    __tablename__ = 'verificacoes_email'

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(120), nullable=False, index=True)
    codigo_hash = db.Column(db.String(64), nullable=False)
    expira = db.Column(db.DateTime, nullable=False)
    tentativas = db.Column(db.Integer, nullable=False, default=0)
    # Usados só no tipo 'cadastro':
    nome = db.Column(db.String(100), nullable=True)
    senha_hash = db.Column(db.String(255), nullable=True)
    perfil = db.Column(db.String(20), nullable=True)
    data = db.Column(db.DateTime, default=datetime.now)
