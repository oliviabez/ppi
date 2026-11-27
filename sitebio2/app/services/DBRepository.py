"""Pequena camada de persistência exclusivamente SQLAlchemy/MySQL."""
from app import db


class DBRepository:
    def __init__(self, model):
        self.model = model

    def adicionar(self, **campos):
        obj = self.model(**campos)
        db.session.add(obj)
        db.session.commit()
        return obj

    def buscar(self, id_):
        return db.session.get(self.model, id_) if id_ is not None else None

    def listar(self, ordenar="id", desc=False, **filtros):
        consulta = self.model.query
        if filtros:
            consulta = consulta.filter_by(**filtros)
        coluna = getattr(self.model, ordenar)
        return consulta.order_by(coluna.desc() if desc else coluna.asc()).all()

    def um(self, **filtros):
        return self.model.query.filter_by(**filtros).first()

    def salvar(self):
        db.session.commit()

    def excluir(self, obj):
        db.session.delete(obj)
        db.session.commit()

    def excluir_onde(self, **filtros):
        for obj in self.model.query.filter_by(**filtros).all():
            db.session.delete(obj)
        db.session.commit()
