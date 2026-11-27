from app import db
from app.constantes import QUIZ_PADRAO_TITULO
from app.models.quiz import ResultadoQuiz


class ResultadoService:
    """Resultados dos estudantes nos quizzes."""

    @staticmethod
    def registrar(usuario_id, acertos, total, quiz_titulo=QUIZ_PADRAO_TITULO):
        novo = ResultadoQuiz(usuario_id=usuario_id, acertos=acertos, total=total,
                             quiz_titulo=quiz_titulo)
        db.session.add(novo)
        db.session.commit()
        return novo

    @staticmethod
    def listar_do_usuario(usuario_id, limite=10):
        return (ResultadoQuiz.query.filter_by(usuario_id=usuario_id)
                .order_by(ResultadoQuiz.data.desc(), ResultadoQuiz.id.desc())
                .limit(limite).all())
