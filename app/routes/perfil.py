"""Atualizar/excluir o próprio cadastro (todos os perfis)."""
from flask import Blueprint, render_template, flash, redirect, url_for, session, g
from app.constantes import PERFIL_ADMIN
from app.forms import PerfilForm, ExcluirContaForm
from app.services import UsuarioService

bp = Blueprint('perfil', __name__)


@bp.route('/perfil', methods=['GET', 'POST'])
def perfil():
    form = PerfilForm(obj=g.usuario)
    eh_admin = g.usuario.perfil == PERFIL_ADMIN
    if form.validate_on_submit():
        outro = UsuarioService.buscar_por_email(form.email.data)
        if outro is not None and outro.id != g.usuario.id:
            form.email.errors = list(form.email.errors) + ["Este e-mail já está em uso por outra conta."]
        elif not UsuarioService.autenticar(g.usuario.email, form.senha_atual.data):
            form.senha_atual.errors = list(form.senha_atual.errors) + ["Senha atual incorreta."]
        elif eh_admin and not UsuarioService.codigo_admin_confere(g.usuario, form.codigo_admin.data):
            form.codigo_admin.errors = list(form.codigo_admin.errors) + ["Código de administrador incorreto."]
        else:
            UsuarioService.atualizar(g.usuario.id, {'nome': form.nome.data, 'email': form.email.data,
                                                    'senha': form.senha_nova.data})
            flash("Cadastro atualizado com sucesso.", "success")
            return redirect(url_for('perfil.perfil'))
    return render_template('shared/perfil.html', form=form, excluir_form=ExcluirContaForm(prefix='excluir'))


@bp.route('/perfil/excluir', methods=['POST'])
def perfil_excluir():
    form = ExcluirContaForm(prefix='excluir')
    if not form.validate_on_submit():
        flash("Digite sua senha para excluir a conta.", "danger")
        return redirect(url_for('perfil.perfil'))
    if not UsuarioService.autenticar(g.usuario.email, form.senha_atual.data):
        flash("Senha incorreta. A conta não foi excluída.", "danger")
        return redirect(url_for('perfil.perfil'))
    # Não deixa o sistema ficar sem nenhum administrador.
    if g.usuario.perfil == PERFIL_ADMIN and UsuarioService.contar_por_perfil()[PERFIL_ADMIN] <= 1:
        flash("Você é o único administrador. Crie outro administrador antes de excluir esta conta.", "danger")
        return redirect(url_for('perfil.perfil'))
    UsuarioService.excluir(g.usuario.id)
    session.clear()
    flash("Sua conta foi excluída.", "info")
    return redirect(url_for('acesso.auth'))
