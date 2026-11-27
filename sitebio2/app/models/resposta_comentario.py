from datetime import datetime
from app import db


class RespostaComentario(db.Model):
    """Resposta de um administrador a uma dúvida (comentário) de estudante."""
    __tablename__ = 'respostas_comentario'

    id = db.Column(db.Integer, primary_key=True)
    comentario_id = db.Column(db.Integer, db.ForeignKey('comentarios.id', ondelete='CASCADE'),
                              nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='SET NULL'),
                         nullable=True)
    admin_nome = db.Column(db.String(100), nullable=False)
    texto = db.Column(db.String(1000), nullable=False)
    data = db.Column(db.DateTime, default=datetime.now)
