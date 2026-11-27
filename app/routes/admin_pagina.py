"""Administrador: editar o texto das páginas de conteúdo fixas (celula, dna...)."""
from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from app.constantes import PERFIL_ADMIN, PAGINAS_FIXAS
from app.services import PaginaService, ImagemService
from app.utils import perfis_permitidos, exigir_csrf

bp = Blueprint('admin_pagina', __name__)


@bp.route('/admin/pagina/<chave>/editar', methods=['GET', 'POST'])
@perfis_permitidos(PERFIL_ADMIN)
def admin_pagina_editar(chave):
    if chave not in PAGINAS_FIXAS:
        abort(404)
    secoes, erro = None, None
    if request.method == 'POST':
        exigir_csrf()
        secoes = PaginaService.ler_secoes(request.form)
        if not secoes:
            erro = "Mantenha ao menos uma seção com texto."
        elif any(not s['titulo'] for s in secoes):
            erro = "Toda seção precisa de um título."
        else:
            PaginaService.salvar(chave, secoes)
            flash("Conteúdo atualizado. Já aparece para os usuários.", "success")
            return redirect(url_for('admin_pagina.admin_pagina_editar', chave=chave))
    if secoes is None:
        secoes = PaginaService.secoes_para_editar(chave)
    return render_template('admin/admin_pagina_editar.html', chave=chave, titulo=PAGINAS_FIXAS[chave][1],
                           rota=PAGINAS_FIXAS[chave][0], secoes=secoes, erro=erro,
                           imagens=ImagemService.listar_pagina(chave),
                           editado=PaginaService.secoes_editadas(chave) is not None)


@bp.route('/admin/pagina/<chave>/restaurar', methods=['POST'])
@perfis_permitidos(PERFIL_ADMIN)
def admin_pagina_restaurar(chave):
    if chave not in PAGINAS_FIXAS:
        abort(404)
    exigir_csrf()
    PaginaService.restaurar(chave)
    flash("Texto original restaurado.", "info")
    return redirect(url_for('admin_pagina.admin_pagina_editar', chave=chave))
