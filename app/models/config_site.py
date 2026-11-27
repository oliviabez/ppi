from app import db


class ConfigSite(db.Model):
    """Pequenas marcações do sistema (ex.: o quiz padrão já foi copiado para o banco?)."""
    __tablename__ = 'config_site'

    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(50), unique=True, nullable=False)
    valor = db.Column(db.String(200))
