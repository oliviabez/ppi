from datetime import datetime
from app import db


class RespostaQuiz(db.Model):
    """Uma resposta dada em um quiz (só de estudantes) — base de 'meus erros' e do plano de estudos."""
    __tablename__ = 'respostas_quiz'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'),
                           nullable=False, index=True)
    resultado_id = db.Column(db.Integer, db.ForeignKey('resultados_quiz.id', ondelete='CASCADE'),
                             nullable=True)
    quiz_titulo = db.Column(db.String(200), nullable=False)
    tema = db.Column(db.String(50), nullable=False)
    enunciado = db.Column(db.Text, nullable=False)
    marcada = db.Column(db.String(1))
    marcada_texto = db.Column(db.String(200))
    correta = db.Column(db.String(1), nullable=False)
    correta_texto = db.Column(db.String(200))
    acertou = db.Column(db.Boolean, nullable=False, default=False)
    data = db.Column(db.DateTime, default=datetime.now)
