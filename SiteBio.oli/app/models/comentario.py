from app import db

class Comentario(db.Model):
    __tablename__ = 'comentarios'

    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(500), nullable=False)
    data = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Chaves estrangeiras
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    publicacao_id = db.Column(db.Integer, db.ForeignKey('publicacoes.id'), nullable=True)

    def __repr__(self):
        return f'<Comentario {self.id}>'
