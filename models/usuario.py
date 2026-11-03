from datetime import datetime
from app import db


class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    #  aqui fica o HASH da senha (werkzeug), nunca a senha pura. O hash do werkzeug
    # (scrypt/pbkdf2) cabe em 200 caracteres; se trocar o algoritmo, confira o tamanho.
    senha = db.Column(db.String(200), nullable=False)
    perfil = db.Column(db.String(20), default='Estudante')   # Estudante | Publico | Admin
    data_cadastro = db.Column(db.DateTime, default=datetime.now)

    # Ao excluir o usuário, seus comentários/feedbacks e resultados de quiz vão junto.
    comentarios = db.relationship('Comentario', backref='autor', lazy=True,
                                  cascade='all, delete-orphan')
    resultados = db.relationship('ResultadoQuiz', backref='aluno', lazy=True,
                                 cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Usuario {self.nome}>'
