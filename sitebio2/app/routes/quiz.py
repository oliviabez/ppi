"""Quizzes, "meus erros" e plano de estudos (lado do estudante/público)."""
from flask import Blueprint, render_template, request, redirect, url_for, g, abort
from app.constantes import PERFIL_ESTUDANTE, PERFIL_ADMIN, TEMAS_CONTEUDO
from app.services import (ConteudoService, ResultadoService, QuizService, RespostaQuizService, PlanoService)
from app.utils import perfis_permitidos, exigir_csrf

bp = Blueprint('quiz', __name__)


@bp.route('/quiz')
def quiz():
    """Quadrinhos: um por conteúdo (tema). Cada um abre os quizzes daquele conteúdo."""
    if g.usuario.perfil == PERFIL_ADMIN:           # admin não faz quiz: cria/edita na área dele
        return redirect(url_for('admin_quiz.admin_quizzes'))
    tema = request.args.get('tema')
    if tema in dict(TEMAS_CONTEUDO):
        return redirect(url_for('quiz.quiz_tema', tema=tema))
    QuizService.garantir_quiz_padrao()
    contagem = {t: 0 for t, _ in TEMAS_CONTEUDO}
    for q in QuizService.listar():
        contagem[q.tema] = contagem.get(q.tema, 0) + 1
    return render_template('quiz/quiz.html', temas=TEMAS_CONTEUDO, contagem=contagem)


@bp.route('/quiz/tema/<tema>')
def quiz_tema(tema):
    if g.usuario.perfil == PERFIL_ADMIN:
        return redirect(url_for('admin_quiz.admin_quiz_tema', tema=tema))
    if tema not in dict(TEMAS_CONTEUDO):
        abort(404)
    QuizService.garantir_quiz_padrao()
    quizzes = [dict(q=q, n=len(QuizService.perguntas_do_quiz(q.id))) for q in QuizService.listar(tema)]
    paginas, publicados = ConteudoService.paginas_do_tema(tema)
    return render_template('quiz/quiz_tema.html', tema=tema, quizzes=quizzes, paginas=paginas,
                           publicados=publicados)


@bp.route('/quiz/<int:quiz_id>', methods=['GET', 'POST'])
def quiz_dinamico(quiz_id):
    """Quiz criado pelo administrador (mesma estrutura do quiz padrão)."""
    if g.usuario.perfil == PERFIL_ADMIN:
        return redirect(url_for('admin_quiz.admin_quizzes'))
    item = QuizService.buscar(quiz_id)
    if item is None:
        abort(404)
    perguntas = QuizService.perguntas_do_quiz(quiz_id)
    marcadas, resultado, detalhes, aviso, salvo = {}, None, None, None, False
    if request.method == 'POST':
        exigir_csrf()
        marcadas = {p.id: request.form.get(f'q{p.id}') for p in perguntas}
        acertos, detalhes, faltando = QuizService.corrigir(item, marcadas)
        if faltando:
            aviso = 'Responda todas as perguntas. Faltam: ' + ', '.join(str(n) for n in faltando) + '.'
            detalhes = None
        else:
            resultado = f"Você acertou {acertos} de {len(perguntas)} perguntas!"
            if g.usuario.perfil == PERFIL_ESTUDANTE:
                salvo_obj = ResultadoService.registrar(g.usuario.id, acertos, len(perguntas),
                                                         quiz_titulo=item.titulo)
                RespostaQuizService.registrar(g.usuario.id, salvo_obj, item.titulo, detalhes)
                salvo = True
    return render_template('quiz/quiz_dinamico.html', quiz=item, perguntas=perguntas, marcadas=marcadas,
                           resultado=resultado, detalhes=detalhes, aviso=aviso, salvo=salvo)


@bp.route('/meus-erros')
@perfis_permitidos(PERFIL_ESTUDANTE)
def meus_erros():
    return render_template('shared/meus_erros.html',
                           erros=RespostaQuizService.erros_do_usuario(g.usuario.id),
                           duvidas=RespostaQuizService.duvidas_por_tema(g.usuario.id))


@bp.route('/plano-de-estudos')
@perfis_permitidos(PERFIL_ESTUDANTE)
def plano_estudos():
    duvidas = RespostaQuizService.duvidas_por_tema(g.usuario.id)
    # tempo disponível por dia e hora de início vêm da URL (?minutos=90&inicio=19:30)
    minutos, inicio = PlanoService.validar_parametros(request.args.get('minutos'), request.args.get('inicio'))
    dias, enfase = PlanoService.montar(duvidas, ConteudoService.listar_todos(), minutos, inicio)
    return render_template('shared/plano.html', dias=dias, enfase=enfase, duvidas=duvidas, minutos=minutos,
                           inicio=inicio, opcoes_minutos=PlanoService.OPCOES_MINUTOS,
                           total_semana=sum(d['total'] for d in dias))
