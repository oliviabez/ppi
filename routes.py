import re
import time
from datetime import datetime, timedelta
from functools import wraps
from flask import (render_template, request, flash, redirect, url_for, session, g, abort)
from werkzeug.security import generate_password_hash
from app import app
from app.constantes import (ROTULO_PERFIL, TEMAS_FEEDBACK, TIPOS_POR_PERFIL,
                            PERFIL_ESTUDANTE, PERFIL_ADMIN, PERFIL_PUBLICO, TEMAS_CONTEUDO,
                            PAGINAS_FIXAS, TEMA_PERGUNTA_FIXA, QUIZ_PADRAO_TITULO, ROTA_POR_TEMA)
from app.forms import (QuizForm, UsuarioForm, LoginForm, PublicacaoForm, ComentarioForm,
                       PerfilForm, ExcluirContaForm, AcaoForm, EsqueciSenhaForm,
                       RedefinirSenhaForm, ConfirmarCadastroForm, ReenviarForm, RespostaForm,
                       ContatoAdminForm)
from app.services import UsuarioService, ConteudoService, FeedbackService, ResultadoService
from app.services import (EmailService, VerificacaoService, ImagemService, RespostaService,
                          QuizService, RespostaQuizService, PlanoService, PaginaService, filtro)

# ══════════════════════════════════════════════════════════════════════════════
#  SESSÃO, LOGIN OBRIGATÓRIO E PERMISSÕES
# ══════════════════════════════════════════════════════════════════════════════

# Únicas rotas acessíveis SEM login. Todas as demais exigem sessão (ver carregar_usuario).
ENDPOINTS_PUBLICOS = {'auth', 'cadastro', 'static', 'esqueci_senha', 'redefinir_senha',
                      'cadastro_confirmar', 'cadastro_reenviar'}


@app.before_request
def carregar_usuario():
    """Roda antes de toda requisição: identifica quem está logado e barra quem não está."""
    g.usuario = None
    if request.endpoint == 'static':
        return
    usuario_id = session.get('usuario_id')
    if usuario_id is not None:
        g.usuario = UsuarioService().buscar_por_id(usuario_id)
        if g.usuario is None:          # conta foi excluída enquanto a sessão estava aberta
            session.clear()
    if request.endpoint is None or request.endpoint in ENDPOINTS_PUBLICOS:
        return
    if g.usuario is None:
        flash("Faça login para acessar o SiteBio.", "info")
        return redirect(url_for('auth'))


@app.context_processor
def variaveis_de_template():
    usuario = getattr(g, 'usuario', None)
    # Imagens que o admin anexou à página FIXA que está aberta (celula, dna...)
    chave = next((k for k, (rota, _, _) in PAGINAS_FIXAS.items() if rota == request.endpoint), None)
    return dict(
        usuario_logado=usuario,
        primeiro_nome=usuario.nome.split()[0] if usuario else '',
        acao_form=AcaoForm(),          # token CSRF para botões de sair/excluir
        imagens_pagina=ImagemService().listar_pagina(chave) if (chave and usuario) else [],
        # texto editado pelo admin (None = mostra o original) e conteúdos publicados do mesmo tema
        secoes_pagina=PaginaService().secoes_editadas(chave) if (chave and usuario) else None,
        conteudos_tema=([c for c in ConteudoService().listar_todos() if c.tema == PAGINAS_FIXAS[chave][2]]
                        if (chave and usuario) else []),
        rota_tema=ROTA_POR_TEMA,
        email_modo_dev=not app.config['SMTP_HOST'],
    )


@app.template_filter('data_br')
def data_br(valor):
    return valor.strftime('%d/%m/%Y %H:%M') if valor else ''


@app.template_filter('rotulo_perfil')
def rotulo_perfil(valor):
    return ROTULO_PERFIL.get(valor, valor)


@app.template_filter('censurar')
def censurar(valor):
    """Palavras obscenas aparecem rasuradas (ver services/filtro.py)."""
    return filtro.censurar(valor)


@app.template_filter('recente')
def recente(data, dias=30):
    """True se a data é de até 'dias' dias atrás (usado no selo 'Novo')."""
    return bool(data) and datetime.now() - data <= timedelta(days=dias)


@app.template_filter('titulo_quiz')
def titulo_quiz(titulo):
    """Tira marcações do tipo '(editável)' do título: elas só devem aparecer para administradores."""
    return re.sub(r'\s*\(\s*edit[aá]vel[^)]*\)', '', titulo or '', flags=re.I).strip()


@app.template_filter('rotulo_tema')
def rotulo_tema(valor):
    return dict(TEMAS_FEEDBACK).get(valor, valor)


def pagina_inicial(usuario):
    """Para onde cada perfil vai depois do login."""
    if usuario.perfil == PERFIL_ADMIN:
        return url_for('admin')
    return url_for('modalidades')          # Estudante e Público externo


def perfis_permitidos(*perfis):
    """Restringe a rota a certos perfis. Se o perfil não puder, responde 403."""
    def decorador(funcao):
        @wraps(funcao)
        def envelope(*args, **kwargs):
            if g.usuario is None or g.usuario.perfil not in perfis:
                abort(403)
            return funcao(*args, **kwargs)
        return envelope
    return decorador


def exigir_csrf():
    """Valida o token CSRF dos formulários simples (sair, excluir)."""
    if not AcaoForm().validate_on_submit():
        abort(400)


@app.errorhandler(403)
def erro_403(_):
    return render_template('erro.html', codigo=403, titulo='Acesso negado',
                           mensagem='Seu perfil não tem permissão para acessar esta página.'), 403


@app.errorhandler(404)
def erro_404(_):
    return render_template('erro.html', codigo=404, titulo='Página não encontrada',
                           mensagem='O endereço que você tentou abrir não existe.'), 404


@app.errorhandler(400)
def erro_400(_):
    return render_template('erro.html', codigo=400, titulo='Requisição inválida',
                           mensagem='Não foi possível validar a solicitação. Volte e tente de novo.'), 400


# ══════════════════════════════════════════════════════════════════════════════
#  LOGIN / CADASTRO / SAIR
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    # Quem não está logado já foi mandado para /auth pelo carregar_usuario().
    return redirect(pagina_inicial(g.usuario))


@app.route('/auth', methods=['GET', 'POST'])
def auth():
    """Tela de login. O cadastro fica em outra tela (/cadastro), acessada por um link."""
    if g.usuario:
        return redirect(pagina_inicial(g.usuario))

    login_form = LoginForm(prefix='login')

    if request.method == 'POST' and login_form.submit.data:
        if login_form.validate_on_submit():
            usuario = UsuarioService().autenticar(login_form.email.data, login_form.senha.data)
            if usuario:
                session.clear()                      # evita reaproveitar sessão antiga
                session['usuario_id'] = usuario.id
                flash(f"Bem-vindo(a), {usuario.nome.split()[0]}!", "success")
                # Redireciona conforme o perfil: Admin -> painel; Estudante/Público -> modalidades
                return redirect(pagina_inicial(usuario))
            # Mensagem única de propósito: não revela se foi o e-mail ou a senha que errou.
            flash("E-mail ou senha incorretos.", "danger")
        else:
            flash("Erro ao realizar login. Preencha os campos corretamente.", "danger")

    return render_template('auth.html', login_form=login_form,
                           mostrar_demo=not app.config['USAR_BANCO'])


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    """Tela de cadastro (separada do login). Ao criar a conta, volta para o login."""
    if g.usuario:
        return redirect(pagina_inicial(g.usuario))

    usuario_form = UsuarioForm(prefix='cad')
    servico = UsuarioService()

    if request.method == 'POST' and usuario_form.submit.data:
        if usuario_form.validate_on_submit():
            erro = False
            if servico.buscar_por_email(usuario_form.email.data):
                usuario_form.email.errors = list(usuario_form.email.errors) + [
                    "Já existe uma conta com este e-mail."]
                erro = True
            if (usuario_form.perfil.data == PERFIL_ADMIN
                    and usuario_form.codigo_admin.data != app.config['ADMIN_CODIGO']):
                usuario_form.codigo_admin.errors = list(usuario_form.codigo_admin.errors) + [
                    "Código de administrador incorreto."]
                erro = True
            if not erro:
                # cria a conta na hora e manda só uma mensagem avisando do cadastro (sem código).
                email = usuario_form.email.data.strip().lower()
                servico.cadastrar({
                    'nome': usuario_form.nome.data,
                    'email': email,
                    'perfil': usuario_form.perfil.data,
                    'senha': usuario_form.senha.data,
                })
                enviado = EmailService().enviar(
                    email, 'Bem-vindo(a) ao SiteBio!',
                    f"Olá, {usuario_form.nome.data.strip().split()[0]}!\n\nSeu cadastro no SiteBio "
                    f"({ROTULO_PERFIL.get(usuario_form.perfil.data)}) foi realizado com sucesso.\n\n"
                    f"Entre em: {url_for('auth', _external=True)}\n\nBons estudos!\nEquipe SiteBio — IFRN\n")
                flash("Conta criada com sucesso! Agora é só entrar com seu e-mail e senha."
                      + ("" if enviado else " (Não foi possível enviar o e-mail de boas-vindas.)"), "success")
                return redirect(url_for('auth'))
        flash("Erro ao cadastrar. Verifique os dados inseridos.", "danger")

    return render_template('cadastro.html', usuario_form=usuario_form)


@app.route('/sair', methods=['POST'])
def sair():
    exigir_csrf()
    session.clear()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for('auth'))


# ══════════════════════════════════════════════════════════════════════════════
#  ÁREA DO ESTUDANTE / PÚBLICO EXTERNO ("suas modalidades")
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/modalidades')
def modalidades():
    resultados, duvidas = [], []
    if g.usuario.perfil == PERFIL_ESTUDANTE:
        resultados = ResultadoService().listar_do_usuario(g.usuario.id, limite=5)
        duvidas = [d for d in RespostaQuizService().duvidas_por_tema(g.usuario.id) if d['erros']][:2]
    return render_template('modalidades.html',
                           conteudos=[c for c in ConteudoService().listar_todos()
                                      if recente(c.data_criacao)],       # aviso de 30 dias
                           resultados=resultados, duvidas=duvidas)


@app.route('/conteudo/<int:conteudo_id>')
def conteudo(conteudo_id):
    item = ConteudoService().buscar(conteudo_id)
    if item is None:
        abort(404)
    return render_template('conteudo.html', conteudo=item,
                           imagens=ImagemService().listar_conteudo(conteudo_id))


# Páginas de conteúdo fixas (estáticas). Todas exigem login (ver carregar_usuario).
@app.route('/celula')
def celula():
    return render_template('celula.html')


@app.route('/citologia')
def citologia():
    return render_template('citologia.html')


@app.route('/dna')
def dna():
    return render_template('dna.html')


@app.route('/continuidade')
def cont():
    return render_template('cont.html')


@app.route('/educacao-sexual')
def ed_sex():
    return render_template('ed.sex.html')


@app.route('/manutencao')
def manutencao():
    return render_template('manutencao.html')


GABARITO_PADRAO = {'q1': 'B', 'q2': 'B', 'q3': 'C', 'q4': 'D', 'q5': 'A'}


def _garantir_quiz_padrao():
    """O quiz padrão (antes fixo no código) é copiado UMA vez para o banco, e a partir daí é um quiz
    comum: o admin pode editar e até apagar (não volta a ser criado)."""
    modelo = QuizForm()
    perguntas = []
    for campo, certa in GABARITO_PADRAO.items():
        f = getattr(modelo, campo)
        t = dict(f.choices)
        perguntas.append({'enunciado': re.sub(r'^\d+\.\s*', '', f.label.text), 'opcao_a': t['A'],
                          'opcao_b': t['B'], 'opcao_c': t['C'], 'opcao_d': t['D'],
                          'resposta_correta': certa})
    QuizService().garantir_padrao(QUIZ_PADRAO_TITULO, 'Célula', perguntas)


def _paginas_do_tema(tema):
    """Páginas de conteúdo fixas + conteúdos publicados que pertencem a um tema."""
    return ([(rota, titulo) for rota, titulo, t in PAGINAS_FIXAS.values() if t == tema],
            [c for c in ConteudoService().listar_todos() if c.tema == tema])


@app.route('/quiz')
def quiz():
    """Quadrinhos: um por conteúdo (tema). Cada um abre os quizzes daquele conteúdo."""
    if g.usuario.perfil == PERFIL_ADMIN:           # admin não faz quiz: cria/edita na área dele
        return redirect(url_for('admin_quizzes'))
    tema = request.args.get('tema')
    if tema in dict(TEMAS_CONTEUDO):
        return redirect(url_for('quiz_tema', tema=tema))
    _garantir_quiz_padrao()
    servico = QuizService()
    contagem = {t: 0 for t, _ in TEMAS_CONTEUDO}
    for q in servico.listar():
        contagem[q.tema] = contagem.get(q.tema, 0) + 1
    return render_template('quiz.html', temas=TEMAS_CONTEUDO, contagem=contagem)


@app.route('/quiz/tema/<tema>')
def quiz_tema(tema):
    if g.usuario.perfil == PERFIL_ADMIN:
        return redirect(url_for('admin_quiz_tema', tema=tema))
    if tema not in dict(TEMAS_CONTEUDO):
        abort(404)
    _garantir_quiz_padrao()
    servico = QuizService()
    quizzes = [dict(q=q, n=len(servico.perguntas_do_quiz(q.id))) for q in servico.listar(tema)]
    paginas, publicados = _paginas_do_tema(tema)
    return render_template('quiz_tema.html', tema=tema, quizzes=quizzes, paginas=paginas,
                           publicados=publicados)


@app.route('/quiz/<int:quiz_id>', methods=['GET', 'POST'])
def quiz_dinamico(quiz_id):
    """Quiz criado pelo administrador (mesma estrutura do quiz padrão)."""
    if g.usuario.perfil == PERFIL_ADMIN:
        return redirect(url_for('admin_quizzes'))
    servico = QuizService()
    item = servico.buscar(quiz_id)
    if item is None:
        abort(404)
    perguntas = servico.perguntas_do_quiz(quiz_id)
    marcadas, resultado, detalhes, aviso, salvo = {}, None, None, None, False
    if request.method == 'POST':
        exigir_csrf()
        marcadas = {p.id: request.form.get(f'q{p.id}') for p in perguntas}
        acertos, detalhes, faltando = servico.corrigir(item, marcadas)
        if faltando:
            aviso = 'Responda todas as perguntas. Faltam: ' + ', '.join(str(n) for n in faltando) + '.'
            detalhes = None
        else:
            resultado = f"Você acertou {acertos} de {len(perguntas)} perguntas!"
            if g.usuario.perfil == PERFIL_ESTUDANTE:
                salvo_obj = ResultadoService().registrar(g.usuario.id, acertos, len(perguntas),
                                                         quiz_titulo=item.titulo)
                RespostaQuizService().registrar(g.usuario.id, salvo_obj, item.titulo, detalhes)
                salvo = True
    return render_template('quiz_dinamico.html', quiz=item, perguntas=perguntas, marcadas=marcadas,
                           resultado=resultado, detalhes=detalhes, aviso=aviso, salvo=salvo)


@app.route('/meus-erros')
@perfis_permitidos('Estudante')
def meus_erros():
    servico = RespostaQuizService()
    return render_template('meus_erros.html', erros=servico.erros_do_usuario(g.usuario.id),
                           duvidas=servico.duvidas_por_tema(g.usuario.id))


@app.route('/plano-de-estudos')
@perfis_permitidos('Estudante')
def plano_estudos():
    duvidas = RespostaQuizService().duvidas_por_tema(g.usuario.id)
    dias, enfase = PlanoService().montar(duvidas, ConteudoService().listar_todos())
    return render_template('plano.html', dias=dias, enfase=enfase, duvidas=duvidas)


# ══════════════════════════════════════════════════════════════════════════════
#  FEEDBACKS E COMENTÁRIOS (Estudante: comentário + feedback | Público: só feedback)
# ══════════════════════════════════════════════════════════════════════════════

def _form_feedback(**kwargs):
    form = ComentarioForm(**kwargs)
    # Define as opções ANTES de validar: público externo só pode escolher "Feedback".
    form.tipo.choices = TIPOS_POR_PERFIL[g.usuario.perfil]
    return form


@app.route('/feedback', methods=['GET', 'POST'])
@perfis_permitidos('Estudante', 'Publico')
def feedback():
    form = _form_feedback()
    servico = FeedbackService()
    previa = None
    if form.validate_on_submit():
        if filtro.tem_palavrao(form.texto.data):
            # texto com palavras obscenas não é publicado; as palavras aparecem rasuradas.
            form.texto.errors = list(form.texto.errors) + [filtro.MENSAGEM_BLOQUEIO]
            previa = filtro.censurar(form.texto.data)
        else:
            servico.adicionar(g.usuario.id, {'tipo': form.tipo.data, 'tema': form.tema.data,
                                             'texto': form.texto.data})
            flash("Mensagem enviada. Obrigado por contribuir!", "success")
            return redirect(url_for('feedback'))
    meus = servico.listar_do_usuario(g.usuario.id)
    return render_template('feedback.html', form=form, editando=False, meus_envios=meus,
                           previa=previa, respostas=RespostaService().mapa(meus))


@app.route('/feedback/<int:comentario_id>/editar', methods=['GET', 'POST'])
@perfis_permitidos('Estudante', 'Publico')
def feedback_editar(comentario_id):
    servico = FeedbackService()
    item = servico.buscar(comentario_id)
    # sempre confirir o DONO do registro, senão qualquer usuário edita o de outro
    # só trocando o número na URL.
    if item is None or item.usuario_id != g.usuario.id:
        abort(404)
    form = _form_feedback(obj=item)
    previa = None
    if form.validate_on_submit():
        if filtro.tem_palavrao(form.texto.data):
            form.texto.errors = list(form.texto.errors) + [filtro.MENSAGEM_BLOQUEIO]
            previa = filtro.censurar(form.texto.data)
        else:
            servico.atualizar(comentario_id, {'tipo': form.tipo.data, 'tema': form.tema.data,
                                              'texto': form.texto.data})
            flash("Mensagem atualizada.", "success")
            return redirect(url_for('feedback'))
    return render_template('feedback.html', form=form, editando=True, meus_envios=[],
                           previa=previa, respostas={})


@app.route('/feedback/<int:comentario_id>/excluir', methods=['POST'])
@perfis_permitidos('Estudante', 'Publico')
def feedback_excluir(comentario_id):
    exigir_csrf()
    servico = FeedbackService()
    item = servico.buscar(comentario_id)
    if item is None or item.usuario_id != g.usuario.id:      # só o dono exclui
        abort(404)
    servico.excluir(comentario_id)
    flash("Mensagem excluída.", "info")
    return redirect(url_for('feedback'))


# ══════════════════════════════════════════════════════════════════════════════
#  PERFIL: ATUALIZAR / EXCLUIR O PRÓPRIO CADASTRO (todos os perfis)
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    servico = UsuarioService()
    form = PerfilForm(obj=g.usuario)
    if form.validate_on_submit():
        outro = servico.buscar_por_email(form.email.data)
        if outro is not None and outro.id != g.usuario.id:
            form.email.errors = list(form.email.errors) + ["Este e-mail já está em uso por outra conta."]
        elif not servico.autenticar(g.usuario.email, form.senha_atual.data):
            form.senha_atual.errors = list(form.senha_atual.errors) + ["Senha atual incorreta."]
        else:
            servico.atualizar(g.usuario.id, {'nome': form.nome.data, 'email': form.email.data,
                                             'senha': form.senha_nova.data})
            flash("Cadastro atualizado com sucesso.", "success")
            return redirect(url_for('perfil'))
    return render_template('perfil.html', form=form, excluir_form=ExcluirContaForm(prefix='excluir'))


@app.route('/perfil/excluir', methods=['POST'])
def perfil_excluir():
    servico = UsuarioService()
    form = ExcluirContaForm(prefix='excluir')
    if not form.validate_on_submit():
        flash("Digite sua senha para excluir a conta.", "danger")
        return redirect(url_for('perfil'))
    if not servico.autenticar(g.usuario.email, form.senha_atual.data):
        flash("Senha incorreta. A conta não foi excluída.", "danger")
        return redirect(url_for('perfil'))
    # Não deixa o sistema ficar sem nenhum administrador.
    if g.usuario.perfil == PERFIL_ADMIN and servico.contar_por_perfil()[PERFIL_ADMIN] <= 1:
        flash("Você é o único administrador. Crie outro administrador antes de excluir esta conta.", "danger")
        return redirect(url_for('perfil'))
    servico.excluir(g.usuario.id)
    session.clear()
    flash("Sua conta foi excluída.", "info")
    return redirect(url_for('auth'))


# ══════════════════════════════════════════════════════════════════════════════
#  ADMIN: conteúdos (criar/editar/excluir) + feedbacks + acompanhamento
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/admin', methods=['GET', 'POST'])
@perfis_permitidos('Admin')
def admin():
    form = PublicacaoForm()
    conteudo_servico = ConteudoService()

    if form.validate_on_submit():
        novo = conteudo_servico.adicionar({'titulo': form.titulo.data, 'tema': form.tema.data,
                                           'descricao': form.descricao.data, 'texto': form.texto.data})
        flash(f"Publicação '{form.titulo.data}' salva com sucesso!", "success")
        _processar_uploads(novo.id, None)          #  imagens enviadas junto com o conteúdo
        return redirect(url_for('admin'))

    feedbacks = FeedbackService().listar_todos()
    tentativas, media = ResultadoService().resumo_geral()
    resumo = {
        'usuarios': UsuarioService().contar_por_perfil(),
        'feedbacks': sum(1 for f in feedbacks if f.tipo == 'Feedback'),
        'comentarios': sum(1 for f in feedbacks if f.tipo == 'Comentario'),
        'tentativas_quiz': tentativas,
        'media_quiz': media,
    }
    todos = UsuarioService().listar_todos()
    admins = [u for u in todos if u.perfil == PERFIL_ADMIN]
    usuarios = {'Estudante': [u for u in todos if u.perfil == PERFIL_ESTUDANTE],
                'Publico': [u for u in todos if u.perfil == PERFIL_PUBLICO],
                'Admin': admins}                       # controle de quem está cadastrado
    return render_template('admin.html', usuarios=usuarios, form=form, conteudos=conteudo_servico.listar_todos(),
                           feedbacks=feedbacks, resumo=resumo, admins=admins,
                           respostas=RespostaService().mapa(feedbacks), paginas_fixas=PAGINAS_FIXAS)


@app.route('/admin/conteudo/<int:conteudo_id>/editar', methods=['GET', 'POST'])
@perfis_permitidos('Admin')
def admin_editar(conteudo_id):
    servico = ConteudoService()
    item = servico.buscar(conteudo_id)
    if item is None:
        abort(404)
    form = PublicacaoForm(obj=item)
    if form.validate_on_submit():
        servico.atualizar(conteudo_id, {'titulo': form.titulo.data, 'tema': form.tema.data,
                                        'descricao': form.descricao.data, 'texto': form.texto.data})
        flash("Conteúdo atualizado.", "success")
        return redirect(url_for('admin'))
    return render_template('admin_editar.html', form=form, conteudo=item,
                           imagens=ImagemService().listar_conteudo(conteudo_id))


@app.route('/admin/conteudo/<int:conteudo_id>/excluir', methods=['POST'])
@perfis_permitidos('Admin')
def admin_excluir(conteudo_id):
    exigir_csrf()
    ImagemService().excluir_do_conteudo(conteudo_id)       # apaga também os arquivos das imagens
    if not ConteudoService().excluir(conteudo_id):
        abort(404)
    flash("Conteúdo excluído.", "info")
    return redirect(url_for('admin'))


# ══════════════════════════════════════════════════════════════════════════════
#  E-MAIL: confirmar cadastro e recuperar senha
# ══════════════════════════════════════════════════════════════════════════════

def _texto_codigo(nome, codigo, motivo):
    primeiro = (nome or '').strip().split()[0] if (nome or '').strip() else 'tudo bem'
    return (f"Olá, {primeiro}!\n\nSeu código para {motivo} no SiteBio é:\n\n        {codigo}\n\n"
            "Ele vale por 15 minutos e só pode ser usado por você. Se não foi você que pediu, "
            "ignore este e-mail.\n\nSiteBio — Plataforma educacional de Biologia · IFRN\n")


@app.route('/cadastro/confirmar', methods=['GET', 'POST'])
def cadastro_confirmar():
    """Passo 2 do cadastro: o código chegou no e-mail? Então a conta é criada."""
    if g.usuario:
        return redirect(pagina_inicial(g.usuario))
    form = ConfirmarCadastroForm(prefix='conf')
    if request.method == 'GET':
        form.email.data = request.args.get('email', '')
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        verificacao = VerificacaoService()
        reg, erro = verificacao.validar('cadastro', email, form.codigo.data)
        if erro:
            form.codigo.errors = list(form.codigo.errors) + [erro]
        elif UsuarioService().buscar_por_email(email):
            verificacao.consumir(reg)
            flash("Este e-mail já tem conta. Entre com sua senha.", "info")
            return redirect(url_for('auth'))
        else:
            UsuarioService().cadastrar({'nome': reg.nome, 'email': email, 'perfil': reg.perfil,
                                        'senha_hash': reg.senha_hash})
            verificacao.consumir(reg)
            EmailService().enviar(
                email, 'Bem-vindo(a) ao SiteBio!',
                f"Olá, {reg.nome.split()[0]}!\n\nSeu e-mail foi confirmado e sua conta no SiteBio "
                f"({ROTULO_PERFIL.get(reg.perfil, reg.perfil)}) está ativa.\n\n"
                f"Entre em: {url_for('auth', _external=True)}\n\nBons estudos!\nEquipe SiteBio — IFRN\n")
            flash("E-mail confirmado e conta criada! Agora é só entrar com seu e-mail e senha.", "success")
            return redirect(url_for('auth'))
    return render_template('cadastro_confirmar.html', form=form, reenviar_form=ReenviarForm(prefix='reenv'))


@app.route('/cadastro/reenviar', methods=['POST'])
def cadastro_reenviar():
    form = ReenviarForm(prefix='reenv')
    if not form.validate_on_submit():
        abort(400)
    email = form.email.data.strip().lower()
    verificacao = VerificacaoService()
    pendente = verificacao.pendente('cadastro', email)
    if pendente is None:
        flash("Não há cadastro pendente para este e-mail. Preencha o cadastro novamente.", "danger")
        return redirect(url_for('cadastro'))
    espera = verificacao.segundos_para_reenviar('cadastro', email)
    if espera:
        flash(f"Aguarde {espera}s para pedir outro código.", "info")
    else:
        codigo = verificacao.gerar('cadastro', email, nome=pendente.nome,
                                   senha_hash=pendente.senha_hash, perfil=pendente.perfil)
        enviado = EmailService().enviar(email, 'SiteBio — novo código de confirmação',
                                        _texto_codigo(pendente.nome, codigo, 'confirmar seu cadastro'))
        flash("Novo código enviado." if enviado else "Não foi possível enviar o e-mail agora.",
              "info" if enviado else "danger")
    return redirect(url_for('cadastro_confirmar', email=email))


@app.route('/esqueci-senha', methods=['GET', 'POST'])
def esqueci_senha():
    if g.usuario:
        return redirect(pagina_inicial(g.usuario))
    form = EsqueciSenhaForm(prefix='esq')
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        usuario = UsuarioService().buscar_por_email(email)
        verificacao = VerificacaoService()
        if usuario and verificacao.segundos_para_reenviar('senha', email) == 0:
            codigo = verificacao.gerar('senha', email)
            EmailService().enviar(email, 'SiteBio — código para criar uma nova senha',
                                  _texto_codigo(usuario.nome, codigo, 'redefinir sua senha'))
        # Mensagem igual exista a conta ou não: não revela quais e-mails estão cadastrados.
        flash("Se este e-mail estiver cadastrado, enviamos um código de 6 números (vale 15 minutos). "
              "Olhe também a caixa de spam.", "info")
        return redirect(url_for('redefinir_senha', email=email))
    return render_template('esqueci_senha.html', form=form)


@app.route('/redefinir-senha', methods=['GET', 'POST'])
def redefinir_senha():
    if g.usuario:
        return redirect(pagina_inicial(g.usuario))
    form = RedefinirSenhaForm(prefix='red')
    if request.method == 'GET':
        form.email.data = request.args.get('email', '')
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        verificacao = VerificacaoService()
        reg, erro = verificacao.validar('senha', email, form.codigo.data)
        usuario = UsuarioService().buscar_por_email(email)
        if erro:
            form.codigo.errors = list(form.codigo.errors) + [erro]
        elif usuario is None:
            form.email.errors = list(form.email.errors) + ["E-mail não encontrado."]
        else:
            UsuarioService().atualizar(usuario.id, {'nome': usuario.nome, 'email': usuario.email,
                                                    'senha': form.senha.data})
            verificacao.consumir(reg)
            flash("Senha alterada com sucesso! Entre com a nova senha.", "success")
            return redirect(url_for('auth'))
    return render_template('redefinir_senha.html', form=form)


# ══════════════════════════════════════════════════════════════════════════════
#  ESTUDANTE escreve para o e-mail de um administrador (fora do site)
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/contato-admin', methods=['GET', 'POST'])
@perfis_permitidos('Estudante')
def contato_admin():
    admins = [u for u in UsuarioService().listar_todos() if u.perfil == PERFIL_ADMIN]
    form = ContatoAdminForm()
    form.admin_id.choices = [(a.id, a.nome) for a in admins]      # o aluno vê só os NOMES
    previa = None
    if form.validate_on_submit():
        destino = next((a for a in admins if a.id == form.admin_id.data), None)
        if filtro.tem_palavrao(form.assunto.data + ' ' + form.mensagem.data):
            form.mensagem.errors = list(form.mensagem.errors) + [filtro.MENSAGEM_BLOQUEIO]
            previa = filtro.censurar(form.assunto.data + '\n' + form.mensagem.data)
        elif time.time() - session.get('contato_ts', 0) < 30:
            flash("Aguarde alguns segundos antes de enviar outra mensagem.", "info")
        elif destino and EmailService().enviar(
                destino.email, f"[SiteBio] {form.assunto.data.strip()}",
                f"Mensagem do(a) estudante {g.usuario.nome} <{g.usuario.email}>:\n\n"
                f"{form.mensagem.data.strip()}\n\n— Enviado pelo SiteBio. Responda este e-mail para falar com o(a) estudante.",
                reply_to=g.usuario.email):
            session['contato_ts'] = time.time()
            flash(f"E-mail enviado para {destino.nome}. A resposta chega no seu e-mail.", "success")
            return redirect(url_for('contato_admin'))
        else:
            flash("Não foi possível enviar o e-mail agora. Tente de novo mais tarde.", "danger")
    return render_template('contato_admin.html', form=form, admins=admins, previa=previa)


# ══════════════════════════════════════════════════════════════════════════════
#  ADMIN: responder dúvidas (avisa o estudante por e-mail)
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/admin/comentario/<int:comentario_id>/responder', methods=['GET', 'POST'])
@perfis_permitidos('Admin')
def admin_responder(comentario_id):
    item = FeedbackService().buscar(comentario_id)
    if item is None or item.tipo != 'Comentario':      # só as dúvidas (comentários) de estudantes
        abort(404)
    autor = UsuarioService().buscar_por_id(item.usuario_id)
    respostas = RespostaService()
    form = RespostaForm()
    previa = None
    if form.validate_on_submit():
        if filtro.tem_palavrao(form.texto.data):
            form.texto.errors = list(form.texto.errors) + [filtro.MENSAGEM_BLOQUEIO]
            previa = filtro.censurar(form.texto.data)
        else:
            respostas.adicionar(comentario_id, g.usuario, form.texto.data)
            enviado = autor is not None and EmailService().enviar(
                autor.email, 'SiteBio — sua dúvida foi respondida',
                f"Olá, {autor.nome.split()[0]}!\n\n{g.usuario.nome} respondeu sua dúvida "
                f"({dict(TEMAS_FEEDBACK).get(item.tema, item.tema)}):\n\n"
                f"Sua dúvida: {item.texto}\n\nResposta: {form.texto.data.strip()}\n\n"
                f"Algo mais específico? Responda este e-mail: ele chega direto para {g.usuario.email}.\n"
                f"Você também vê a resposta no site: {url_for('feedback', _external=True)}\n\n"
                "Equipe SiteBio — IFRN\n",
                reply_to=g.usuario.email)
            if enviado:
                flash("Resposta salva e estudante avisado por e-mail.", "success")
            else:
                flash("Resposta salva, mas NÃO foi possível avisar o estudante por e-mail.", "danger")
            return redirect(url_for('admin_responder', comentario_id=comentario_id))
    return render_template('admin_responder.html', form=form, item=item, autor=autor, previa=previa,
                           respostas=respostas.listar_do_comentario(comentario_id))


# ══════════════════════════════════════════════════════════════════════════════
#   ADMIN: imagens dos conteúdos (publicados e páginas fixas)
# ══════════════════════════════════════════════════════════════════════════════

def _processar_uploads(conteudo_id, pagina):
    salvas, erros = ImagemService().salvar_uploads(
        request.files.getlist('imagens'), request.form.get('legenda_imagens', ''),
        conteudo_id=conteudo_id, pagina=pagina)
    if salvas:
        flash(f"{salvas} imagem(ns) adicionada(s).", "success")
    for erro in erros:
        flash(erro, "danger")
    return salvas


@app.route('/admin/conteudo/<int:conteudo_id>/imagens', methods=['POST'])
@perfis_permitidos('Admin')
def admin_imagens_conteudo(conteudo_id):
    exigir_csrf()
    if ConteudoService().buscar(conteudo_id) is None:
        abort(404)
    if not _processar_uploads(conteudo_id, None) and not request.files.getlist('imagens')[0].filename:
        flash("Escolha ao menos uma imagem.", "info")
    return redirect(url_for('admin_editar', conteudo_id=conteudo_id))


@app.route('/admin/pagina/<chave>/imagens', methods=['GET', 'POST'])
@perfis_permitidos('Admin')
def admin_pagina_imagens(chave):
    if chave not in PAGINAS_FIXAS:
        abort(404)
    if request.method == 'POST':
        exigir_csrf()
        if not _processar_uploads(None, chave) and not request.files.getlist('imagens')[0].filename:
            flash("Escolha ao menos uma imagem.", "info")
        return redirect(url_for('admin_pagina_imagens', chave=chave))
    rota, titulo, _ = PAGINAS_FIXAS[chave]
    return render_template('admin_pagina_imagens.html', chave=chave, titulo=titulo, rota=rota,
                           imagens=ImagemService().listar_pagina(chave))


@app.route('/admin/imagem/<int:imagem_id>/excluir', methods=['POST'])
@perfis_permitidos('Admin')
def admin_imagem_excluir(imagem_id):
    exigir_csrf()
    servico = ImagemService()
    img = servico.buscar(imagem_id)
    if img is None:
        abort(404)
    conteudo_id, pagina = img.conteudo_id, img.pagina
    servico.excluir(img)
    flash("Imagem removida.", "info")
    if conteudo_id:
        return redirect(url_for('admin_editar', conteudo_id=conteudo_id))
    return redirect(url_for('admin_pagina_imagens', chave=pagina))


# ══════════════════════════════════════════════════════════════════════════════
#  ADMIN: criar/editar quizzes (um por conteúdo) + porcentagens (só o admin vê)
# ══════════════════════════════════════════════════════════════════════════════

def _ler_perguntas_form():
    """Lê as perguntas do formulário: p<N>_enunciado, p<N>_a..d, p<N>_correta, p<N>_id."""
    perguntas, erros = [], []
    total = min(request.form.get('total', type=int) or 0, 40)
    for i in range(1, total + 1):
        if f'p{i}_enunciado' not in request.form:      # bloco removido na tela
            continue
        d = {'enunciado': request.form.get(f'p{i}_enunciado', '').strip(),
             'opcao_a': request.form.get(f'p{i}_a', '').strip(),
             'opcao_b': request.form.get(f'p{i}_b', '').strip(),
             'opcao_c': request.form.get(f'p{i}_c', '').strip(),
             'opcao_d': request.form.get(f'p{i}_d', '').strip(),
             'resposta_correta': request.form.get(f'p{i}_correta', ''),
             'id': request.form.get(f'p{i}_id', type=int)}
        vazio = not any(d[k] for k in ('enunciado', 'opcao_a', 'opcao_b', 'opcao_c', 'opcao_d'))
        if vazio and d['id'] is None:
            continue                                    # bloco em branco: ignora
        if (not all(d[k] for k in ('enunciado', 'opcao_a', 'opcao_b', 'opcao_c', 'opcao_d'))
                or d['resposta_correta'] not in ('A', 'B', 'C', 'D')):
            erros.append(f"Pergunta {len(perguntas) + 1}: preencha o enunciado, as 4 alternativas e marque a correta.")
        elif len(d['enunciado']) > 1000 or any(len(d[k]) > 200 for k in ('opcao_a', 'opcao_b', 'opcao_c', 'opcao_d')):
            erros.append(f"Pergunta {len(perguntas) + 1}: texto grande demais (alternativas até 200 caracteres).")
        perguntas.append(d)
    return perguntas, erros


@app.route('/admin/quizzes')
@perfis_permitidos('Admin')
def admin_quizzes():
    """Quadrinhos: um por conteúdo (tema). Cada um abre os quizzes daquele conteúdo."""
    _garantir_quiz_padrao()
    servico = QuizService()
    por_quiz = {q['titulo']: q for q in RespostaQuizService().por_quiz()}
    cartoes = []
    for tema, rotulo in TEMAS_CONTEUDO:
        qs = servico.listar(tema)
        tentativas = sum(por_quiz[q.titulo]['tentativas'] for q in qs if q.titulo in por_quiz)
        media = (round(sum(por_quiz[q.titulo]['media'] * por_quiz[q.titulo]['tentativas']
                           for q in qs if q.titulo in por_quiz) / tentativas) if tentativas else None)
        cartoes.append(dict(tema=tema, rotulo=rotulo, n=len(qs), tentativas=tentativas, media=media))
    return render_template('admin_quizzes.html', cartoes=cartoes)


@app.route('/admin/quizzes/tema/<tema>')
@perfis_permitidos('Admin')
def admin_quiz_tema(tema):
    """Quizzes de UM conteúdo: criar vários, editar, excluir e ver as porcentagens."""
    if tema not in dict(TEMAS_CONTEUDO):
        abort(404)
    _garantir_quiz_padrao()
    servico = QuizService()
    stats = RespostaQuizService()
    por_quiz = {q['titulo']: q for q in stats.por_quiz()}
    quizzes = [dict(q=q, n=len(servico.perguntas_do_quiz(q.id)), stat=por_quiz.get(q.titulo))
               for q in servico.listar(tema)]
    titulos = {i['q'].titulo for i in quizzes}
    paginas, publicados = _paginas_do_tema(tema)
    return render_template('admin_quiz_tema.html', tema=tema, quizzes=quizzes, paginas=paginas,
                           publicados=publicados,
                           por_pergunta=[p for p in stats.por_pergunta() if p['quiz'] in titulos])


def _form_quiz(quiz=None):
    """Mostra/valida o formulário de quiz. Devolve (resposta, ...) para as duas rotas abaixo."""
    servico = QuizService()
    erros, perguntas = [], None
    titulo = quiz.titulo if quiz else ''
    tema_url = request.args.get('tema')
    tema = quiz.tema if quiz else (tema_url if tema_url in dict(TEMAS_CONTEUDO) else TEMAS_CONTEUDO[0][0])
    if request.method == 'POST':
        exigir_csrf()
        titulo = request.form.get('titulo', '').strip()
        tema = request.form.get('tema', '')
        perguntas, erros = _ler_perguntas_form()
        if not titulo or len(titulo) > 200:
            erros.append("Informe o título do quiz (até 200 caracteres).")
        elif servico.titulo_existe(titulo, ignorar_id=quiz.id if quiz else None):
            erros.append("Já existe um quiz com este título. Use outro (as estatísticas são separadas por título).")
        if tema not in dict(TEMAS_CONTEUDO):
            erros.append("Escolha o conteúdo (tema) do quiz.")
        if not perguntas:
            erros.append("Adicione ao menos uma pergunta.")
        if not erros:
            if quiz:
                servico.atualizar(quiz, titulo, tema, perguntas)
                flash("Quiz atualizado.", "success")
            else:
                servico.criar(titulo, tema, perguntas)
                flash(f"Quiz '{titulo}' criado.", "success")
            return redirect(url_for('admin_quiz_tema', tema=tema))
    elif quiz:
        perguntas = [dict(id=p.id, enunciado=p.enunciado, opcao_a=p.opcao_a, opcao_b=p.opcao_b,
                          opcao_c=p.opcao_c, opcao_d=p.opcao_d, resposta_correta=p.resposta_correta)
                     for p in servico.perguntas_do_quiz(quiz.id)]
    if not perguntas:
        perguntas = [dict(id=None, enunciado='', opcao_a='', opcao_b='', opcao_c='', opcao_d='',
                          resposta_correta='') for _ in range(5)]       # mesma estrutura: 5 perguntas
    return render_template('admin_quiz_form.html', quiz=quiz, titulo=titulo, tema=tema,
                           perguntas=perguntas, erros=erros)


@app.route('/admin/quizzes/novo', methods=['GET', 'POST'])
@perfis_permitidos('Admin')
def admin_quiz_novo():
    return _form_quiz()


@app.route('/admin/quizzes/<int:quiz_id>/editar', methods=['GET', 'POST'])
@perfis_permitidos('Admin')
def admin_quiz_editar(quiz_id):
    quiz_obj = QuizService().buscar(quiz_id)
    if quiz_obj is None:
        abort(404)
    return _form_quiz(quiz_obj)


@app.route('/admin/quizzes/<int:quiz_id>/excluir', methods=['POST'])
@perfis_permitidos('Admin')
def admin_quiz_excluir(quiz_id):
    exigir_csrf()
    servico = QuizService()
    quiz_obj = servico.buscar(quiz_id)
    if quiz_obj is None:
        abort(404)
    tema = quiz_obj.tema
    servico.excluir(quiz_obj)
    flash("Quiz excluído.", "info")
    return redirect(url_for('admin_quiz_tema', tema=tema))


# ══════════════════════════════════════════════════════════════════════════════
#  ADMIN: editar o texto das páginas de conteúdo fixas (celula, dna...)
# ══════════════════════════════════════════════════════════════════════════════

def _ler_secoes_form():
    """Lê as seções do formulário: s<N>_titulo / s<N>_html."""
    secoes = []
    total = min(request.form.get('total', type=int) or 0, 40)
    for i in range(1, total + 1):
        if f'u{i}_titulo' not in request.form:          # seção removida na tela
            continue
        titulo = request.form.get(f'u{i}_titulo', '').strip()
        html = request.form.get(f'u{i}_html', '').strip()
        if titulo or html:
            secoes.append({'titulo': titulo, 'html': html})
    return secoes


@app.route('/admin/pagina/<chave>/editar', methods=['GET', 'POST'])
@perfis_permitidos('Admin')
def admin_pagina_editar(chave):
    if chave not in PAGINAS_FIXAS:
        abort(404)
    servico = PaginaService()
    secoes, erro = None, None
    if request.method == 'POST':
        exigir_csrf()
        secoes = _ler_secoes_form()
        if not secoes:
            erro = "Mantenha ao menos uma seção com texto."
        elif any(not s['titulo'] for s in secoes):
            erro = "Toda seção precisa de um título."
        else:
            servico.salvar(chave, secoes)
            flash("Conteúdo atualizado. Já aparece para os usuários.", "success")
            return redirect(url_for('admin_pagina_editar', chave=chave))
    if secoes is None:
        secoes = servico.secoes_para_editar(chave)
    return render_template('admin_pagina_editar.html', chave=chave, titulo=PAGINAS_FIXAS[chave][1],
                           rota=PAGINAS_FIXAS[chave][0], secoes=secoes, erro=erro,
                           editado=servico.secoes_editadas(chave) is not None)


@app.route('/admin/pagina/<chave>/restaurar', methods=['POST'])
@perfis_permitidos('Admin')
def admin_pagina_restaurar(chave):
    if chave not in PAGINAS_FIXAS:
        abort(404)
    exigir_csrf()
    PaginaService().restaurar(chave)
    flash("Texto original restaurado.", "info")
    return redirect(url_for('admin_pagina_editar', chave=chave))
