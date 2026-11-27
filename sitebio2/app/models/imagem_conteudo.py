from datetime import datetime
from app import db


class ImagemConteudo(db.Model):
    """Imagem anexada a um conteúdo publicado (conteudo_id) OU a uma página fixa (pagina)."""
    __tablename__ = 'imagens_conteudo'

    id = db.Column(db.Integer, primary_key=True)
    conteudo_id = db.Column(db.Integer, db.ForeignKey('conteudos.id', ondelete='CASCADE'),
                            nullable=True)
    pagina = db.Column(db.String(30), nullable=True)      # celula | citologia | dna | cont | ed_sex | manutencao
    arquivo = db.Column(db.String(100), nullable=False)   # nome do arquivo em static/uploads/
    legenda = db.Column(db.String(200))
    data = db.Column(db.DateTime, default=datetime.now)
