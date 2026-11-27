"""Ganchos da aplicação: sessão/login obrigatório, variáveis de template e páginas de erro."""
from flask import render_template, request, flash, redirect, url_for, session, g
from app import app
from app.constantes import PAGINAS_FIXAS, ROTA_POR_TEMA, MENU_CONTEUDOS
from app.forms import AcaoForm
from app.services import UsuarioService, ConteudoService, ImagemService, PaginaService, imagem_texto

# Únicas rotas acessíveis SEM login. Todas as demais exigem sessão (ver carregar_usuario).
ENDPOINTS_PUBLICOS = {'acesso.auth', 'acesso.cadastro', 'acesso.confirmar_cadastro', 'static',
                      'acesso.esqueci_senha', 'acesso.redefinir_senha'}


@app.before_request
def carregar_usuario():
    """Roda antes de toda requisição: identifica quem está logado e barra quem não está."""
    g.usuario = None
    if request.endpoint == 'static':
        return
    usuario_id = session.get('usuario_id')
    if usuario_id is not None:
        g.usuario = UsuarioService.buscar_por_id(usuario_id)
        if g.usuario is None:          # conta foi excluída enquanto a sessão estava aberta
            session.clear()
    if request.endpoint is None or request.endpoint in ENDPOINTS_PUBLICOS:
        return
    if g.usuario is None:
        flash("Faça login para acessar o SiteBio.", "info")
        return redirect(url_for('acesso.auth'))


@app.context_processor
def variaveis_de_template():
    usuario = getattr(g, 'usuario', None)
    # Imagens que o admin anexou à página FIXA que está aberta (celula, dna...)
    chave = next((k for k, (rota, _, _) in PAGINAS_FIXAS.items() if rota == request.endpoint), None)
    pagina = bool(chave and usuario)
    imagens = ImagemService.listar_pagina(chave) if pagina else []
    # texto editado pelo admin (None = mostra o original)
    secoes = PaginaService.secoes_editadas(chave) if pagina else None
    return dict(
        usuario_logado=usuario,
        primeiro_nome=usuario.nome.split()[0] if usuario else '',
        acao_form=AcaoForm(),          # token CSRF para botões de sair/excluir
        imagens_pagina=imagens,
        # imagens que o texto NÃO citou com [imagem N]: vão para o final da página
        imagens_livres=imagem_texto.livres(imagens, [s['html'] for s in secoes or []]),
        secoes_pagina=secoes,
        # conteúdos publicados do mesmo tema
        conteudos_tema=([c for c in ConteudoService.listar_todos() if c.tema == PAGINAS_FIXAS[chave][2]]
                        if (chave and usuario) else []),
        rota_tema=ROTA_POR_TEMA,
        menu_conteudos=MENU_CONTEUDOS,
        email_modo_dev=not app.config['SMTP_HOST'],
    )


@app.errorhandler(403)
def erro_403(_):
    return render_template('shared/erro.html', codigo=403, titulo='Acesso negado',
                           mensagem='Seu perfil não tem permissão para acessar esta página.'), 403


@app.errorhandler(404)
def erro_404(_):
    return render_template('shared/erro.html', codigo=404, titulo='Página não encontrada',
                           mensagem='O endereço que você tentou abrir não existe.'), 404


@app.errorhandler(413)
def erro_413(_):
    return render_template('shared/erro.html', codigo=413, titulo='Arquivo grande demais',
                           mensagem='O envio passou do limite de 16 MB. Envie menos imagens por vez.'), 413


@app.errorhandler(400)
def erro_400(_):
    return render_template('shared/erro.html', codigo=400, titulo='Requisição inválida',
                           mensagem='Não foi possível validar a solicitação. Volte e tente de novo.'), 400
