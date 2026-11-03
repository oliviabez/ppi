from datetime import datetime
from app import db


class Quiz(db.Model):
    __tablename__ = 'quizzes'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    tema = db.Column(db.String(50), nullable=False)

    perguntas = db.relationship('Pergunta', backref='quiz', lazy=True)

    def __repr__(self):
        return f'<Quiz {self.titulo}>'


class Pergunta(db.Model):
    __tablename__ = 'perguntas'

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    enunciado = db.Column(db.Text, nullable=False)
    opcao_a = db.Column(db.String(200), nullable=False)
    opcao_b = db.Column(db.String(200), nullable=False)
    opcao_c = db.Column(db.String(200), nullable=False)
    opcao_d = db.Column(db.String(200), nullable=False)
    resposta_correta = db.Column(db.String(1), nullable=False)

    def __repr__(self):
        return f'<Pergunta {self.id}>'


class ResultadoQuiz(db.Model):
    """Resultado de um aluno em um quiz (item 6 do documento: 'Resultados dos alunos')."""
    __tablename__ = 'resultados_quiz'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    quiz_titulo = db.Column(db.String(200), nullable=False, default='Biologia Celular')
    acertos = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)          # erros = total - acertos
    data = db.Column(db.DateTime, default=datetime.now)

    # LIMITAÇÃO: o quiz atual é fixo no código (QuizForm, 5 perguntas); as tabelas Quiz/Pergunta
    # ainda não são usadas. Por isso aqui guardamos o título em texto, e não uma FK para quizzes.
    # TODO(BANCO): quando o quiz vier do banco, trocar quiz_titulo por quiz_id (FK para quizzes.id).
