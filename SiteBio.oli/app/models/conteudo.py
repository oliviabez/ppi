from app import db

class Conteudo(db.Model):
    __tablename__ = 'conteudos'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.String(500))
    tema = db.Column(db.String(50), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<Conteudo {self.titulo}>'
