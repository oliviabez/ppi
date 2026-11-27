"""Respostas do administrador às dúvidas (comentários) dos estudantes."""
from app.models.resposta_comentario import RespostaComentario
from app.services.DBRepository import DBRepository

_repo = DBRepository(RespostaComentario)


class RespostaService:
    @staticmethod
    def adicionar(comentario_id, admin, texto):
        return _repo.adicionar(comentario_id=comentario_id, admin_id=admin.id,
                               admin_nome=admin.nome, texto=texto.strip())

    @staticmethod
    def listar_do_comentario(comentario_id):
        return _repo.listar(ordenar='data', comentario_id=comentario_id)

    @classmethod
    def mapa(cls, comentarios):
        """{id do comentário: [respostas]} para mostrar nas listas."""
        return {c.id: cls.listar_do_comentario(c.id) for c in comentarios}
