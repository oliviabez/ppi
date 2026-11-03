from datetime import datetime
from flask import current_app
from app.models.quiz import ResultadoQuiz
from app.services import memoria
from app.services.memoria import Registro


def _usar_banco():
    return current_app.config['USAR_BANCO']


class ResultadoService:
    """Resultados dos estudantes nos quizzes."""

    def registrar(self, usuario_id, acertos, total, quiz_titulo='Biologia Celular'):
        if _usar_banco():
            from app import db
            novo = ResultadoQuiz(usuario_id=usuario_id, acertos=acertos, total=total,
                                 quiz_titulo=quiz_titulo)
            db.session.add(novo)
            db.session.commit()
            return novo
        novo = Registro(id=memoria.proximo_id('resultados'), usuario_id=usuario_id, acertos=acertos,
                        total=total, quiz_titulo=quiz_titulo, data=datetime.now())
        memoria.RESULTADOS.append(novo)
        return novo

    def listar_do_usuario(self, usuario_id, limite=10):
        if _usar_banco():
            return (ResultadoQuiz.query.filter_by(usuario_id=usuario_id)
                    .order_by(ResultadoQuiz.data.desc(), ResultadoQuiz.id.desc()).limit(limite).all())
        return [r for r in reversed(memoria.RESULTADOS) if r.usuario_id == usuario_id][:limite]

    def resumo_geral(self):
        """(tentativas, média de acertos em %) de todos os alunos, para o painel do admin."""
        if _usar_banco():
            itens = ResultadoQuiz.query.all()
        else:
            itens = memoria.RESULTADOS
        if not itens:
            return 0, 0
        media = sum(r.acertos / r.total for r in itens if r.total) / len(itens) * 100
        return len(itens), round(media)
