from app import db
from app.models.comentario import Comentario


class FeedbackService:
    """Comentários de estudantes e feedbacks de estudantes/público."""

    @staticmethod
    def adicionar(usuario_id, dados):
        novo = Comentario(usuario_id=usuario_id, tipo=dados["tipo"], tema=dados["tema"],
                          texto=dados["texto"].strip(), permite_publicar=bool(dados.get("permite_publicar")))
        db.session.add(novo)
        db.session.commit()
        return novo

    @staticmethod
    def listar_todos():
        return Comentario.query.order_by(Comentario.data.desc(), Comentario.id.desc()).all()

    @staticmethod
    def listar_do_usuario(usuario_id):
        return (Comentario.query.filter_by(usuario_id=usuario_id)
                .order_by(Comentario.data.desc(), Comentario.id.desc()).all())

    @staticmethod
    def listar_publicados(limite=6):
        """Mensagens que o admin escolheu mostrar no site (só se o autor permitiu)."""
        return (Comentario.query.filter_by(publicado=True, permite_publicar=True)
                .order_by(Comentario.data.desc(), Comentario.id.desc()).limit(limite).all())

    @staticmethod
    def buscar(comentario_id):
        return db.session.get(Comentario, comentario_id)

    @classmethod
    def atualizar(cls, comentario_id, dados):
        item = cls.buscar(comentario_id)
        if item is None:
            return None
        permite = bool(dados.get("permite_publicar"))
        mudou = (item.tipo, item.tema, item.texto) != (dados["tipo"], dados["tema"], dados["texto"].strip())
        item.tipo, item.tema, item.texto = dados["tipo"], dados["tema"], dados["texto"].strip()
        item.permite_publicar = permite
        if mudou or not permite:          # texto alterado ou autorização retirada: sai do ar até nova aprovação
            item.publicado = False
        db.session.commit()
        return item

    @classmethod
    def definir_publicado(cls, item, publicado):
        """O admin publica/retira. Só publica se o autor permitiu. Devolve True se aplicou."""
        if publicado and not item.permite_publicar:
            return False
        item.publicado = bool(publicado)
        db.session.commit()
        return True

    @classmethod
    def excluir(cls, comentario_id):
        item = cls.buscar(comentario_id)
        if item is None:
            return False
        db.session.delete(item)
        db.session.commit()
        return True
