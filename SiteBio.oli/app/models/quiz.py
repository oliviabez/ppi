from app import db

class Quiz(db.Model):
    __tablename__ = 'quizzes'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    tema = db.Column(db.String(50), nullable=False)

    # Relacionamento com as perguntas
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
