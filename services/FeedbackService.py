from datetime import datetime
from flask import current_app
from app.models.comentario import Comentario
from app.services import memoria
from app.services.memoria import Registro


def _usar_banco():
    return current_app.config['USAR_BANCO']


class FeedbackService:
    """Comentários (estudantes) e feedbacks (estudantes e público externo)."""

    def adicionar(self, usuario_id, dados):
        if _usar_banco():
            from app import db
            novo = Comentario(usuario_id=usuario_id, tipo=dados['tipo'],
                              tema=dados['tema'], texto=dados['texto'].strip())
            db.session.add(novo)
            db.session.commit()
            return novo
        novo = Registro(id=memoria.proximo_id('comentarios'), usuario_id=usuario_id,
                        tipo=dados['tipo'], tema=dados['tema'], texto=dados['texto'].strip(),
                        data=datetime.now())
        memoria.COMENTARIOS.append(novo)
        return novo

    def _com_autor(self, itens):
        """No modo memória, anexa o autor (no banco isso já vem pelo relacionamento 'autor')."""
        from app.services.UsuarioService import UsuarioService
        servico = UsuarioService()
        return [Registro(i, autor=servico.buscar_por_id(i.usuario_id)) for i in itens]

    def listar_todos(self):
        """Todos os envios, mais recentes primeiro (uso do administrador)."""
        if _usar_banco():
            return Comentario.query.order_by(Comentario.data.desc(), Comentario.id.desc()).all()
        return self._com_autor(reversed(memoria.COMENTARIOS))

    def listar_do_usuario(self, usuario_id):
        if _usar_banco():
            return (Comentario.query.filter_by(usuario_id=usuario_id)
                    .order_by(Comentario.data.desc(), Comentario.id.desc()).all())
        return [c for c in reversed(memoria.COMENTARIOS) if c.usuario_id == usuario_id]

    def buscar(self, comentario_id):
        if _usar_banco():
            from app import db
            return db.session.get(Comentario, comentario_id)
        return next((c for c in memoria.COMENTARIOS if c.id == comentario_id), None)

    def atualizar(self, comentario_id, dados):
        item = self.buscar(comentario_id)
        if item is None:
            return None
        item.tipo = dados['tipo']
        item.tema = dados['tema']
        item.texto = dados['texto'].strip()
        if _usar_banco():
            from app import db
            db.session.commit()
        return item

    def excluir(self, comentario_id):
        item = self.buscar(comentario_id)
        if item is None:
            return False
        if _usar_banco():
            from app import db
            db.session.delete(item)
            db.session.commit()
        else:
            memoria.COMENTARIOS.remove(item)
        return True
