from datetime import datetime
from app import db


class Comentario(db.Model):
    """Comentário (só estudantes) ou feedback (estudantes e público externo)."""
    __tablename__ = 'comentarios'

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False, default='Feedback')   # Feedback | Comentario
    tema = db.Column(db.String(50), nullable=False, default='Site')
    texto = db.Column(db.String(500), nullable=False)
    data = db.Column(db.DateTime, default=datetime.now)

    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    # LIMITAÇÃO: o envio é ligado a um TEMA (Célula, DNA...), não a um conteúdo específico.
    # E só o autor e os administradores enxergam os envios (não há mural público de comentários).

    def __repr__(self):
        return f'<Comentario {self.id}>'
