"""Feedbacks e comentários (Estudante: comentário + feedback | Público: só feedback) e contato com o admin."""
import time
from flask import Blueprint, render_template, flash, redirect, url_for, session, g, abort
from app.constantes import TIPOS_POR_PERFIL, PERFIL_ESTUDANTE, PERFIL_ADMIN, PERFIL_PUBLICO
from app.forms import ComentarioForm, ContatoAdminForm
from app.services import (UsuarioService, FeedbackService, EmailService, RespostaService, filtro, mensagens_email)
from app.utils import perfis_permitidos, exigir_csrf

bp = Blueprint('feedback', __name__)


def _form_feedback(**kwargs):
    form = ComentarioForm(**kwargs)
    # Define as opções ANTES de validar: público externo só pode escolher "Feedback".
    form.tipo.choices = TIPOS_POR_PERFIL[g.usuario.perfil]
    return form


@bp.route('/feedback', methods=['GET', 'POST'])
@perfis_permitidos(PERFIL_ESTUDANTE, PERFIL_PUBLICO)
def feedback():
    form = _form_feedback()
    previa = None
    if form.validate_on_submit():
        # texto com palavras obscenas não é publicado; as palavras aparecem rasuradas.
        previa = filtro.bloquear_se_palavrao(form.texto, form.texto.data)
        if previa is None:
            FeedbackService.adicionar(g.usuario.id, {'tipo': form.tipo.data, 'tema': form.tema.data,
                                                     'texto': form.texto.data,
                                                     'permite_publicar': form.permite_publicar.data})
            flash("Mensagem enviada. Obrigado por contribuir!", "success")
            return redirect(url_for('feedback.feedback'))
    meus = FeedbackService.listar_do_usuario(g.usuario.id)
    return render_template('shared/feedback.html', form=form, editando=False, meus_envios=meus,
                           previa=previa, respostas=RespostaService.mapa(meus))


@bp.route('/feedback/<int:comentario_id>/editar', methods=['GET', 'POST'])
@perfis_permitidos(PERFIL_ESTUDANTE, PERFIL_PUBLICO)
def feedback_editar(comentario_id):
    item = FeedbackService.buscar(comentario_id)
    # sempre conferir o DONO do registro, senão qualquer usuário edita o de outro
    # só trocando o número na URL.
    if item is None or item.usuario_id != g.usuario.id:
        abort(404)
    form = _form_feedback(obj=item)
    previa = None
    if form.validate_on_submit():
        previa = filtro.bloquear_se_palavrao(form.texto, form.texto.data)
        if previa is None:
            FeedbackService.atualizar(comentario_id, {'tipo': form.tipo.data, 'tema': form.tema.data,
                                                      'texto': form.texto.data,
                                                      'permite_publicar': form.permite_publicar.data})
            flash("Mensagem atualizada.", "success")
            return redirect(url_for('feedback.feedback'))
    return render_template('shared/feedback.html', form=form, editando=True, meus_envios=[],
                           previa=previa, respostas={})


@bp.route('/feedback/<int:comentario_id>/excluir', methods=['POST'])
@perfis_permitidos(PERFIL_ESTUDANTE, PERFIL_PUBLICO)
def feedback_excluir(comentario_id):
    exigir_csrf()
    item = FeedbackService.buscar(comentario_id)
    if item is None or item.usuario_id != g.usuario.id:      # só o dono exclui
        abort(404)
    FeedbackService.excluir(comentario_id)
    flash("Mensagem excluída.", "info")
    return redirect(url_for('feedback.feedback'))


@bp.route('/contato-admin', methods=['GET', 'POST'])
@perfis_permitidos(PERFIL_ESTUDANTE)
def contato_admin():
    admins = [u for u in UsuarioService.listar_todos() if u.perfil == PERFIL_ADMIN]
    form = ContatoAdminForm()
    form.admin_id.choices = [(a.id, a.nome) for a in admins]      # o aluno vê só os NOMES
    previa = None
    if form.validate_on_submit():
        destino = next((a for a in admins if a.id == form.admin_id.data), None)
        previa = filtro.bloquear_se_palavrao(form.mensagem, form.assunto.data + '\n' + form.mensagem.data)
        if previa is None:             # sem palavrão: segue para o envio
            if time.time() - session.get('contato_ts', 0) < 30:
                flash("Aguarde alguns segundos antes de enviar outra mensagem.", "info")
            elif destino and EmailService.enviar(
                    destino.email, f"[SiteBio] {form.assunto.data.strip()}",
                    mensagens_email.contato_estudante(g.usuario, form.mensagem.data),
                    reply_to=g.usuario.email):
                session['contato_ts'] = time.time()
                flash(f"E-mail enviado para {destino.nome}. A resposta chega no seu e-mail.", "success")
                return redirect(url_for('feedback.contato_admin'))
            else:
                flash("Não foi possível enviar o e-mail agora. Tente de novo mais tarde.", "danger")
    return render_template('shared/contato_admin.html', form=form, admins=admins, previa=previa)
