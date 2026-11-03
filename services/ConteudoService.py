from datetime import datetime
from flask import current_app
from app.models.conteudo import Conteudo
from app.services import memoria
from app.services.memoria import Registro


def _usar_banco():
    return current_app.config['USAR_BANCO']


class ConteudoService:
    """Conteúdos educativos publicados pelo administrador."""

    def adicionar(self, dados):
        if _usar_banco():
            from app import db
            novo = Conteudo(titulo=dados['titulo'].strip(), tema=dados['tema'],
                            descricao=(dados.get('descricao') or '').strip() or None,
                            texto=dados['texto'])
            db.session.add(novo)
            db.session.commit()
            return novo
        novo = Registro(id=memoria.proximo_id('conteudos'), titulo=dados['titulo'].strip(),
                        tema=dados['tema'], descricao=(dados.get('descricao') or '').strip() or None,
                        texto=dados['texto'], data_criacao=datetime.now())
        memoria.CONTEUDOS.append(novo)
        return novo

    def listar_todos(self):
        """Mais recentes primeiro."""
        if _usar_banco():
            return Conteudo.query.order_by(Conteudo.data_criacao.desc(), Conteudo.id.desc()).all()
        return list(reversed(memoria.CONTEUDOS))

    def buscar(self, conteudo_id):
        if _usar_banco():
            from app import db
            return db.session.get(Conteudo, conteudo_id)
        return next((c for c in memoria.CONTEUDOS if c.id == conteudo_id), None)

    def atualizar(self, conteudo_id, dados):
        conteudo = self.buscar(conteudo_id)
        if conteudo is None:
            return None
        conteudo.titulo = dados['titulo'].strip()
        conteudo.tema = dados['tema']
        conteudo.descricao = (dados.get('descricao') or '').strip() or None
        conteudo.texto = dados['texto']
        if _usar_banco():
            from app import db
            db.session.commit()
        return conteudo

    def excluir(self, conteudo_id):
        conteudo = self.buscar(conteudo_id)
        if conteudo is None:
            return False
        if _usar_banco():
            from app import db
            db.session.delete(conteudo)
            db.session.commit()
        else:
            memoria.CONTEUDOS.remove(conteudo)
        return True
