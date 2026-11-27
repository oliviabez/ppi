from datetime import datetime
from app import db


class Conteudo(db.Model):
    """Conteúdo educativo publicado pelo administrador."""
    __tablename__ = 'conteudos'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.String(500))
    tema = db.Column(db.String(50), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.now)

    # Quem publicou. O nome fica guardado em texto para continuar aparecendo se a conta for excluída.
    autor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True)
    autor_nome = db.Column(db.String(100), nullable=True)

    # As imagens do conteúdo ficam na tabela imagens_conteudo (ver models/imagem_conteudo.py).
    # LIMITAÇÃO: ainda não há envio de PDFs, só imagens.

    def __repr__(self):
        return f'<Conteudo {self.titulo}>'
