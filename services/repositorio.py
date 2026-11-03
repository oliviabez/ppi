"""Repositório genérico: o mesmo código funciona em MODO MEMÓRIA e no BANCO (SQLAlchemy).

Usado só pelos serviços NOVOS; os serviços antigos continuam exatamente como estavam.
"""
from datetime import datetime
from flask import current_app
from app.services import memoria
from app.services.memoria import Registro


class Repositorio:
    def __init__(self, modelo, nome, padroes=None):
        self.modelo = modelo
        self.nome = nome
        self.padroes = padroes or {}      # valores padrão do modo memória (o banco usa o default da coluna)

    def _banco(self):
        return current_app.config['USAR_BANCO']

    def adicionar(self, **campos):
        if self._banco():
            from app import db
            novo = self.modelo(**campos)
            db.session.add(novo)
            db.session.commit()
            return novo
        reg = Registro(id=memoria.proximo_id(self.nome))
        for chave, valor in self.padroes.items():
            reg[chave] = valor() if callable(valor) else valor
        reg.update(campos)
        memoria.tabela(self.nome).append(reg)
        return reg

    def buscar(self, id_):
        if id_ is None:
            return None
        if self._banco():
            from app import db
            return db.session.get(self.modelo, id_)
        return next((r for r in memoria.tabela(self.nome) if r.id == id_), None)

    def listar(self, ordenar='id', desc=False, **filtros):
        if self._banco():
            consulta = self.modelo.query
            if filtros:
                consulta = consulta.filter_by(**filtros)
            coluna = getattr(self.modelo, ordenar)
            return consulta.order_by(coluna.desc() if desc else coluna.asc()).all()
        itens = [r for r in memoria.tabela(self.nome)
                 if all(r.get(k) == v for k, v in filtros.items())]
        return sorted(itens, key=lambda r: (r.get(ordenar) is None, r.get(ordenar)), reverse=desc)

    def um(self, **filtros):
        itens = self.listar(**filtros)
        return itens[0] if itens else None

    def contar(self, **filtros):
        return len(self.listar(**filtros))

    def salvar(self):
        """Grava alterações feitas em um objeto já carregado (no modo memória não precisa)."""
        if self._banco():
            from app import db
            db.session.commit()

    def excluir(self, obj):
        if self._banco():
            from app import db
            db.session.delete(obj)
            db.session.commit()
        else:
            lista = memoria.tabela(self.nome)
            if obj in lista:
                lista.remove(obj)

    def excluir_onde(self, **filtros):
        for obj in self.listar(**filtros):
            self.excluir(obj)


def agora():
    return datetime.now()
