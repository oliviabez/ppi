"""Administrador: conteúdos, imagens e respostas às dúvidas."""
from flask import Blueprint, render_template, request, flash, redirect, url_for, g, abort, jsonify
from app.constantes import PERFIL_ESTUDANTE, PERFIL_ADMIN, PERFIL_PUBLICO, PAGINAS_FIXAS, TIPO_COMENTARIO
from app.forms import PublicacaoForm, RespostaForm
from app.services import (UsuarioService, ConteudoService, FeedbackService, EmailService, ImagemService,
                          RespostaService, PaginaService, filtro, mensagens_email)
from app.utils import perfis_permitidos, exigir_csrf, recente

bp = Blueprint('admin', __name__)


def _ajax():
    """O editor visual envia/remove imagens sem recarregar a página (e sem perder o texto digitado)."""
    return request.headers.get('X-Requested-With') == 'fetch'


def _imagem_json(img):
    return {'id': img.id, 'url': url_for('static', filename='uploads/' + img.arquivo),
            'legenda': img.legenda or '', 'excluir_url': url_for('admin.admin_imagem_excluir', imagem_id=img.id)}


def _upload_ajax(conteudo_id, pagina):
    listar = (lambda: ImagemService.listar_conteudo(conteudo_id)) if conteudo_id else \
             (lambda: ImagemService.listar_pagina(pagina))
    arquivos = request.files.getlist('imagens')
    if not any(arq.filename for arq in arquivos):
        return jsonify(imagens=[], erros=["Escolha ao menos uma imagem."])
    antes = {i.id for i in listar()}
    _, erros = ImagemService.salvar_uploads(arquivos, request.form.get('legenda_imagens', ''),
                                            conteudo_id=conteudo_id, pagina=pagina)
    return jsonify(imagens=[_imagem_json(i) for i in listar() if i.id not in antes], erros=erros)


def _processar_uploads_ou_avisar(conteudo_id, pagina):
    """Salva as imagens enviadas; se nenhum arquivo foi escolhido, avisa o admin."""
    if not any(arq.filename for arq in request.files.getlist('imagens')):
        flash("Escolha ao menos uma imagem.", "info")
        return
    _processar_uploads(conteudo_id, pagina)


def _processar_uploads(conteudo_id, pagina):
    salvas, erros = ImagemService.salvar_uploads(
        request.files.getlist('imagens'), request.form.get('legenda_imagens', ''),
        conteudo_id=conteudo_id, pagina=pagina)
    if salvas:
        flash(f"{salvas} imagem(ns) adicionada(s).", "success")
    for erro in erros:
        flash(erro, "danger")
    return salvas


@bp.route('/admin', methods=['GET', 'POST'])
@perfis_permitidos(PERFIL_ADMIN)
def admin():
    form = PublicacaoForm()
    texto, erro_texto = '', None

    if request.method == 'POST':
        texto = ConteudoService.ler_texto(request.form)      # mantém o que foi digitado se algo der errado
        if form.validate_on_submit():
            if not texto:
                erro_texto = "Escreva o texto do conteúdo."
            else:
                novo = ConteudoService.adicionar(
                    {'titulo': form.titulo.data, 'tema': form.tema.data, 'descricao': form.descricao.data,
                     'texto': texto}, autor=g.usuario)
                flash(f"Publicação '{form.titulo.data}' salva com sucesso!", "success")
                _processar_uploads(novo.id, None)          # imagens enviadas junto com o conteúdo
                return redirect(url_for('admin.admin'))

    feedbacks = FeedbackService.listar_todos()
    conteudos = ConteudoService.listar_todos()
    todos = UsuarioService.listar_todos()
    usuarios = {PERFIL_ESTUDANTE: [u for u in todos if u.perfil == PERFIL_ESTUDANTE],
                PERFIL_PUBLICO: [u for u in todos if u.perfil == PERFIL_PUBLICO],
                PERFIL_ADMIN: [u for u in todos if u.perfil == PERFIL_ADMIN]}   # controle de quem está cadastrado
    # conteúdos novos (7 dias) publicados por OUTRO administrador: aviso para este admin
    novos_de_outros = [c for c in conteudos if c.autor_id != g.usuario.id and recente(c.data_criacao, 7)]
    return render_template('admin/admin.html', usuarios=usuarios, form=form, texto=texto, erro_texto=erro_texto,
                           conteudos=conteudos, novos_de_outros=novos_de_outros, feedbacks=feedbacks,
                           respostas=RespostaService.mapa(feedbacks), paginas_fixas=PAGINAS_FIXAS)


@bp.route('/admin/conteudo/<int:conteudo_id>/editar', methods=['GET', 'POST'])
@perfis_permitidos(PERFIL_ADMIN)
def admin_editar(conteudo_id):
    item = ConteudoService.buscar(conteudo_id)
    if item is None:
        abort(404)
    form = PublicacaoForm(obj=item)
    texto, erro_texto = item.texto, None
    if request.method == 'POST':
        texto = ConteudoService.ler_texto(request.form)
        if form.validate_on_submit():
            if not texto:
                erro_texto = "Escreva o texto do conteúdo."
            else:
                ConteudoService.atualizar(conteudo_id, {'titulo': form.titulo.data, 'tema': form.tema.data,
                                                        'descricao': form.descricao.data, 'texto': texto})
                flash("Conteúdo atualizado.", "success")
                return redirect(url_for('admin.admin'))
    return render_template('admin/admin_editar.html', form=form, conteudo=item, texto=texto,
                           erro_texto=erro_texto, imagens=ImagemService.listar_conteudo(conteudo_id))


@bp.route('/admin/conteudo/<int:conteudo_id>/excluir', methods=['POST'])
@perfis_permitidos(PERFIL_ADMIN)
def admin_excluir(conteudo_id):
    exigir_csrf()
    ImagemService.excluir_do_conteudo(conteudo_id)       # apaga também os arquivos das imagens
    if not ConteudoService.excluir(conteudo_id):
        abort(404)
    flash("Conteúdo excluído.", "info")
    return redirect(url_for('admin.admin'))


@bp.route('/admin/comentario/<int:comentario_id>/responder', methods=['GET', 'POST'])
@perfis_permitidos(PERFIL_ADMIN)
def admin_responder(comentario_id):
    item = FeedbackService.buscar(comentario_id)
    if item is None or item.tipo != TIPO_COMENTARIO:      # só as dúvidas (comentários) de estudantes
        abort(404)
    autor = UsuarioService.buscar_por_id(item.usuario_id)
    form = RespostaForm()
    previa = None
    if form.validate_on_submit():
        previa = filtro.bloquear_se_palavrao(form.texto, form.texto.data)
        if previa is None:
            RespostaService.adicionar(comentario_id, g.usuario, form.texto.data)
            enviado = autor is not None and EmailService.enviar(
                autor.email, 'SiteBio — sua dúvida foi respondida',
                mensagens_email.resposta_duvida(autor, g.usuario, item, form.texto.data,
                                                url_for('feedback.feedback', _external=True)),
                reply_to=g.usuario.email)
            if enviado:
                flash("Resposta salva e estudante avisado por e-mail.", "success")
            else:
                flash("Resposta salva, mas NÃO foi possível avisar o estudante por e-mail.", "danger")
            return redirect(url_for('admin.admin_responder', comentario_id=comentario_id))
    return render_template('admin/admin_responder.html', form=form, item=item, autor=autor, previa=previa,
                           respostas=RespostaService.listar_do_comentario(comentario_id))


@bp.route('/admin/conteudo/<int:conteudo_id>/imagens', methods=['POST'])
@perfis_permitidos(PERFIL_ADMIN)
def admin_imagens_conteudo(conteudo_id):
    exigir_csrf()
    if ConteudoService.buscar(conteudo_id) is None:
        abort(404)
    if _ajax():
        return _upload_ajax(conteudo_id, None)
    _processar_uploads_ou_avisar(conteudo_id, None)
    return redirect(url_for('admin.admin_editar', conteudo_id=conteudo_id))


@bp.route('/admin/pagina/<chave>/imagens', methods=['GET', 'POST'])
@perfis_permitidos(PERFIL_ADMIN)
def admin_pagina_imagens(chave):
    if chave not in PAGINAS_FIXAS:
        abort(404)
    if request.method == 'POST':
        exigir_csrf()
        if _ajax():
            return _upload_ajax(None, chave)
        _processar_uploads_ou_avisar(None, chave)
        return redirect(url_for('admin.admin_pagina_imagens', chave=chave))
    rota, titulo, _ = PAGINAS_FIXAS[chave]
    return render_template('admin/admin_pagina_imagens.html', chave=chave, titulo=titulo, rota=rota,
                           imagens=ImagemService.listar_pagina(chave))


@bp.route('/admin/imagem/<int:imagem_id>/excluir', methods=['POST'])
@perfis_permitidos(PERFIL_ADMIN)
def admin_imagem_excluir(imagem_id):
    exigir_csrf()
    img = ImagemService.buscar(imagem_id)
    if img is None:
        abort(404)
    conteudo_id, pagina = img.conteudo_id, img.pagina
    lista = ImagemService.listar_conteudo(conteudo_id) if conteudo_id else ImagemService.listar_pagina(pagina)
    numero = next(i for i, outra in enumerate(lista, start=1) if outra.id == img.id)
    ImagemService.excluir(img)
    # o texto acompanha: some a marcação desta imagem e as seguintes sobem um número
    if conteudo_id:
        ConteudoService.ajustar_marcas(conteudo_id, numero)
    else:
        PaginaService.ajustar_marcas(pagina, numero)
    if _ajax():
        return jsonify(ok=True)
    flash("Imagem removida.", "info")
    if conteudo_id:
        return redirect(url_for('admin.admin_editar', conteudo_id=conteudo_id))
    return redirect(url_for('admin.admin_pagina_imagens', chave=pagina))


@bp.route('/admin/feedback/<int:comentario_id>/publicar', methods=['POST'])
@perfis_permitidos(PERFIL_ADMIN)
def admin_feedback_publicar(comentario_id):
    """Mostra (ou retira) uma mensagem na página inicial. Só vale se o autor permitiu a publicação."""
    exigir_csrf()
    item = FeedbackService.buscar(comentario_id)
    if item is None:
        abort(404)
    publicar = request.form.get('acao') == 'publicar'
    if not FeedbackService.definir_publicado(item, publicar):
        flash("O autor não autorizou a publicação desta mensagem.", "danger")
    else:
        flash("Mensagem publicada no site." if publicar else "Mensagem retirada do site.", "success" if publicar else "info")
    return redirect(url_for('admin.admin') + '#feedbacks')
