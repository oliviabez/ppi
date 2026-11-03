"""Erros/acertos por pergunta: alimenta 'Meus erros' (aluno), plano de estudos e % do admin."""
from datetime import datetime
from app.models.extras import RespostaQuiz
from app.models.quiz import ResultadoQuiz
from app.services.repositorio import Repositorio

_respostas = Repositorio(RespostaQuiz, 'respostas_quiz', padroes={'data': datetime.now})
_resultados = Repositorio(ResultadoQuiz, 'resultados')


class RespostaQuizService:
    def registrar(self, usuario_id, resultado, quiz_titulo, detalhes):
        for d in detalhes:
            _respostas.adicionar(usuario_id=usuario_id, resultado_id=getattr(resultado, 'id', None),
                                 quiz_titulo=quiz_titulo, tema=d['tema'], enunciado=d['enunciado'],
                                 marcada=d['marcada'], marcada_texto=d['marcada_texto'],
                                 correta=d['correta'], correta_texto=d['correta_texto'],
                                 acertou=d['acertou'])

    # ── aluno: SEM porcentagens, só contagens ─────────────────────────────────
    def erros_do_usuario(self, usuario_id, limite=60):
        erros = [r for r in _respostas.listar(ordenar='data', desc=True, usuario_id=usuario_id)
                 if not r.acertou]
        return erros[:limite]

    def duvidas_por_tema(self, usuario_id):
        """[{'tema', 'erros', 'respondidas'}] ordenado de quem tem MAIS erros para o menor."""
        mapa = {}
        for r in _respostas.listar(usuario_id=usuario_id):
            item = mapa.setdefault(r.tema, {'tema': r.tema, 'erros': 0, 'respondidas': 0})
            item['respondidas'] += 1
            item['erros'] += 0 if r.acertou else 1
        return sorted(mapa.values(), key=lambda i: (-i['erros'], -i['respondidas']))

    # ── admin: agregado, com porcentagens (nada pessoal) ───────────────────────
    def por_quiz(self):
        """[{'titulo', 'tentativas', 'media'}] — média de acertos em % de todos os alunos."""
        grupos = {}
        for r in _resultados.listar():
            g = grupos.setdefault(r.quiz_titulo, [])
            g.append(r.acertos / r.total if r.total else 0)
        return sorted(({'titulo': t, 'tentativas': len(v), 'media': round(sum(v) / len(v) * 100)}
                       for t, v in grupos.items()), key=lambda i: i['titulo'])

    def por_pergunta(self):
        """[{'quiz', 'enunciado', 'tema', 'respostas', 'acerto'}] — % de acerto de cada pergunta."""
        grupos = {}
        for r in _respostas.listar():
            g = grupos.setdefault((r.quiz_titulo, r.enunciado), {'tema': r.tema, 'n': 0, 'ok': 0})
            g['n'] += 1
            g['ok'] += 1 if r.acertou else 0
        itens = [{'quiz': q, 'enunciado': e, 'tema': g['tema'], 'respostas': g['n'],
                  'acerto': round(g['ok'] / g['n'] * 100)} for (q, e), g in grupos.items()]
        return sorted(itens, key=lambda i: (i['acerto'], i['quiz']))      # as mais difíceis primeiro
