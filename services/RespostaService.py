"""Respostas do administrador às dúvidas (comentários) dos estudantes."""
from datetime import datetime
from app.models.extras import RespostaComentario
from app.services.repositorio import Repositorio

_repo = Repositorio(RespostaComentario, 'respostas_comentario', padroes={'data': datetime.now})


class RespostaService:
    def adicionar(self, comentario_id, admin, texto):
        return _repo.adicionar(comentario_id=comentario_id, admin_id=admin.id,
                               admin_nome=admin.nome, texto=texto.strip())

    def listar_do_comentario(self, comentario_id):
        return _repo.listar(ordenar='data', comentario_id=comentario_id)

    def mapa(self, comentarios):
        """{id do comentário: [respostas]} para mostrar nas listas."""
        return {c.id: self.listar_do_comentario(c.id) for c in comentarios}
