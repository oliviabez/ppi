from datetime import datetime
from app import db


class Conteudo(db.Model):
    """Conteúdo educativo publicado pelo administrador (substitui o antigo model Publicacao)."""
    __tablename__ = 'conteudos'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.String(500))
    tema = db.Column(db.String(50), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.now)

    # TODO(BANCO): o documento prevê PDFs e imagens ligados ao conteúdo. Quando for implementar,
    # criar uma tabela "arquivos" (nome, titulo, tema, caminho, data) com FK para conteudos.id.
    # LIMITAÇÃO: por enquanto o conteúdo é só texto.

    def __repr__(self):
        return f'<Conteudo {self.titulo}>'
