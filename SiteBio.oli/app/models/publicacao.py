from app import db

class Publicacao(db.Model):
    __tablename__ = 'publicacoes'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    tema = db.Column(db.String(50), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    data = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Chave estrangeira ligada ao utilizador/autor
    autor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # Relacionamento com comentários
    comentarios = db.relationship('Comentario', backref='publicacao', lazy=True)

    def __repr__(self):
        return f'<Publicacao {self.titulo}>'
