from datetime import datetime
from app import db


class PaginaEditada(db.Model):
    """Texto editado pelo admin de uma página de conteúdo FIXA (celula, dna...).
    Enquanto não existir linha aqui, a página mostra o texto original do template."""
    __tablename__ = 'paginas_editadas'

    id = db.Column(db.Integer, primary_key=True)
    pagina = db.Column(db.String(30), unique=True, nullable=False)
    secoes = db.Column(db.Text, nullable=False)          # JSON: [{"titulo": "...", "html": "..."}]
    data = db.Column(db.DateTime, default=datetime.now)
