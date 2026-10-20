from app import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    perfil = db.Column(db.String(20), default='Estudante')

    # Relacionamentos
    comentarios = db.relationship('Comentario', backref='autor', lazy=True)
    publicacoes = db.relationship('Publicacao', backref='autor', lazy=True)

    def __repr__(self):
        return f'<Usuario {self.nome}>'