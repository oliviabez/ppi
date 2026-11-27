"""Administrador: criar/editar quizzes (um por conteúdo) + porcentagens (só o admin vê)."""
from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from app.constantes import PERFIL_ADMIN, TEMAS_CONTEUDO
from app.services import ConteudoService, QuizService, RespostaQuizService
from app.utils import perfis_permitidos, exigir_csrf

bp = Blueprint('admin_quiz', __name__)


def _form_quiz(quiz=None):
    """Mostra/valida o formulário de quiz. Usado pelas rotas de criar e de editar."""
    erros, perguntas = [], None
    titulo = quiz.titulo if quiz else ''
    tema_url = request.args.get('tema')
    tema = quiz.tema if quiz else (tema_url if tema_url in dict(TEMAS_CONTEUDO) else TEMAS_CONTEUDO[0][0])
    if request.method == 'POST':
        exigir_csrf()
        titulo = request.form.get('titulo', '').strip()
        tema = request.form.get('tema', '')
        perguntas, erros = QuizService.ler_perguntas(request.form)
        erros += QuizService.validar_dados(titulo, tema, perguntas, ignorar_id=quiz.id if quiz else None)
        if not erros:
            if quiz:
                QuizService.atualizar(quiz, titulo, tema, perguntas)
                flash("Quiz atualizado.", "success")
            else:
                QuizService.criar(titulo, tema, perguntas)
                flash(f"Quiz '{titulo}' criado.", "success")
            return redirect(url_for('admin_quiz.admin_quiz_tema', tema=tema))
    elif quiz:
        perguntas = QuizService.perguntas_para_edicao(quiz)
    if not perguntas:
        perguntas = QuizService.perguntas_em_branco()
    return render_template('admin/admin_quiz_form.html', quiz=quiz, titulo=titulo, tema=tema,
                           temas=TEMAS_CONTEUDO, perguntas=perguntas, erros=erros)


@bp.route('/admin/quizzes')
@perfis_permitidos(PERFIL_ADMIN)
def admin_quizzes():
    """Quadrinhos: um por conteúdo (tema). Cada um abre os quizzes daquele conteúdo."""
    QuizService.garantir_quiz_padrao()
    por_quiz = {q['titulo']: q for q in RespostaQuizService.por_quiz()}
    cartoes = []
    for tema, rotulo in TEMAS_CONTEUDO:
        qs = QuizService.listar(tema)
        tentativas = sum(por_quiz[q.titulo]['tentativas'] for q in qs if q.titulo in por_quiz)
        media = (round(sum(por_quiz[q.titulo]['media'] * por_quiz[q.titulo]['tentativas']
                           for q in qs if q.titulo in por_quiz) / tentativas) if tentativas else None)
        cartoes.append(dict(tema=tema, rotulo=rotulo, n=len(qs), tentativas=tentativas, media=media))
    return render_template('admin/admin_quizzes.html', cartoes=cartoes)


@bp.route('/admin/quizzes/tema/<tema>')
@perfis_permitidos(PERFIL_ADMIN)
def admin_quiz_tema(tema):
    """Quizzes de UM conteúdo: criar vários, editar, excluir e ver as porcentagens."""
    if tema not in dict(TEMAS_CONTEUDO):
        abort(404)
    QuizService.garantir_quiz_padrao()
    por_quiz = {q['titulo']: q for q in RespostaQuizService.por_quiz()}
    quizzes = [dict(q=q, n=len(QuizService.perguntas_do_quiz(q.id)), stat=por_quiz.get(q.titulo))
               for q in QuizService.listar(tema)]
    titulos = {i['q'].titulo for i in quizzes}
    paginas, publicados = ConteudoService.paginas_do_tema(tema)
    return render_template('admin/admin_quiz_tema.html', tema=tema, quizzes=quizzes, paginas=paginas,
                           publicados=publicados,
                           por_pergunta=[p for p in RespostaQuizService.por_pergunta() if p['quiz'] in titulos])


@bp.route('/admin/quizzes/novo', methods=['GET', 'POST'])
@perfis_permitidos(PERFIL_ADMIN)
def admin_quiz_novo():
    return _form_quiz()


@bp.route('/admin/quizzes/<int:quiz_id>/editar', methods=['GET', 'POST'])
@perfis_permitidos(PERFIL_ADMIN)
def admin_quiz_editar(quiz_id):
    quiz_obj = QuizService.buscar(quiz_id)
    if quiz_obj is None:
        abort(404)
    return _form_quiz(quiz_obj)


@bp.route('/admin/quizzes/<int:quiz_id>/excluir', methods=['POST'])
@perfis_permitidos(PERFIL_ADMIN)
def admin_quiz_excluir(quiz_id):
    exigir_csrf()
    quiz_obj = QuizService.buscar(quiz_id)
    if quiz_obj is None:
        abort(404)
    tema = quiz_obj.tema
    QuizService.excluir(quiz_obj)
    flash("Quiz excluído.", "info")
    return redirect(url_for('admin_quiz.admin_quiz_tema', tema=tema))
