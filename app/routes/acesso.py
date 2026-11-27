"""Login, cadastro (com confirmação do e-mail), sair e recuperação de senha."""
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, g
from app.forms import UsuarioForm, LoginForm, EsqueciSenhaForm, ConfirmarCadastroForm, RedefinirSenhaForm
from app.services import UsuarioService, EmailService, VerificacaoService, mensagens_email
from app.utils import exigir_csrf, pagina_inicial

bp = Blueprint('acesso', __name__)


@bp.route('/')
def index():
    # Quem não está logado já foi mandado para /auth pelo carregar_usuario().
    return redirect(pagina_inicial(g.usuario))


@bp.route('/auth', methods=['GET', 'POST'])
def auth():
    """Tela de login. O cadastro fica em outra tela (/cadastro), acessada por um link."""
    if g.usuario:
        return redirect(pagina_inicial(g.usuario))

    login_form = LoginForm(prefix='login')

    if request.method == 'POST' and login_form.submit.data:
        if login_form.validate_on_submit():
            usuario = UsuarioService.autenticar(login_form.email.data, login_form.senha.data)
            # Administrador também precisa do código pessoal; quem não é admin ignora o campo.
            if usuario and UsuarioService.codigo_admin_confere(usuario, login_form.codigo_admin.data):
                session.clear()                      # evita reaproveitar sessão antiga
                session['usuario_id'] = usuario.id
                flash(f"Bem-vindo(a), {usuario.nome.split()[0]}!", "success")
                # Redireciona conforme o perfil: Admin -> painel; Estudante/Público -> modalidades
                return redirect(pagina_inicial(usuario))
            # Mensagem única de propósito: não revela se foi o e-mail, a senha ou o código que errou.
            flash("E-mail, senha ou código de administrador incorretos.", "danger")
        else:
            flash("Erro ao realizar login. Preencha os campos corretamente.", "danger")

    return render_template('auth/auth.html', login_form=login_form)


def _enviar_codigo_de_cadastro(form):
    """Guarda os dados do cadastro e manda o código ao e-mail. Devolve o e-mail se enviou, senão None."""
    email = form.email.data.strip().lower()
    espera = VerificacaoService.segundos_para_reenviar('cadastro', email)
    if espera:
        flash(f"Já enviamos um código para este e-mail. Aguarde {espera} s para pedir outro.", "info")
        return None
    codigo = VerificacaoService.gerar(
        'cadastro', email, nome=form.nome.data.strip(), perfil=form.perfil.data,
        senha_hash=UsuarioService.gerar_hash(form.senha.data))
    if not EmailService.enviar(email, 'SiteBio — confirme seu e-mail',
                               mensagens_email.codigo_verificacao(form.nome.data, codigo, 'confirmar seu cadastro')):
        VerificacaoService.cancelar('cadastro', email)
        flash("Não foi possível enviar o e-mail de confirmação. Confira o endereço e tente de novo.", "danger")
        return None
    return email


@bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    """Passo 1: dados do cadastro. O código enviado ao e-mail (passo 2) confirma que o e-mail existe."""
    if g.usuario:
        return redirect(pagina_inicial(g.usuario))

    usuario_form = UsuarioForm(prefix='cad')

    if request.method == 'POST' and usuario_form.submit.data:
        if usuario_form.validate_on_submit():
            erros = UsuarioService.validar_cadastro(usuario_form.email.data, usuario_form.perfil.data,
                                                    usuario_form.codigo_admin.data)
            for campo, mensagem in erros.items():
                campo_form = getattr(usuario_form, campo)
                campo_form.errors = list(campo_form.errors) + [mensagem]
            if not erros:
                email = _enviar_codigo_de_cadastro(usuario_form)
                if email:
                    flash(f"Enviamos um código de 6 números para {email} (vale 15 minutos). "
                          "Digite-o abaixo para criar a conta. Olhe também a caixa de spam.", "info")
                    return redirect(url_for('acesso.confirmar_cadastro', email=email))
                return render_template('auth/cadastro.html', usuario_form=usuario_form)
        flash("Erro ao cadastrar. Verifique os dados inseridos.", "danger")

    return render_template('auth/cadastro.html', usuario_form=usuario_form)


@bp.route('/cadastro/confirmar', methods=['GET', 'POST'])
def confirmar_cadastro():
    """Passo 2: o código recebido por e-mail. Só aqui a conta é criada."""
    if g.usuario:
        return redirect(pagina_inicial(g.usuario))
    form = ConfirmarCadastroForm(prefix='conf')
    if request.method == 'GET':
        form.email.data = request.args.get('email', '')
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        reg, erro = VerificacaoService.validar('cadastro', email, form.codigo.data)
        if erro:
            form.codigo.errors = list(form.codigo.errors) + [erro]
        elif UsuarioService.buscar_por_email(email):
            VerificacaoService.consumir(reg)
            form.email.errors = list(form.email.errors) + ["Já existe uma conta com este e-mail."]
        else:
            usuario = UsuarioService.cadastrar_de_verificacao(reg)
            VerificacaoService.consumir(reg)
            enviado = EmailService.enviar(
                email, 'Bem-vindo(a) ao SiteBio!',
                mensagens_email.boas_vindas_cadastro(usuario.nome, usuario.perfil,
                                                     url_for('acesso.auth', _external=True)))
            flash("E-mail confirmado e conta criada com sucesso! Agora é só entrar."
                  + ("" if enviado else " (Não foi possível enviar o e-mail de boas-vindas.)"), "success")
            return redirect(url_for('acesso.auth'))
    return render_template('auth/confirmar_cadastro.html', form=form)


@bp.route('/sair', methods=['POST'])
def sair():
    exigir_csrf()
    session.clear()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for('acesso.auth'))


@bp.route('/esqueci-senha', methods=['GET', 'POST'])
def esqueci_senha():
    if g.usuario:
        return redirect(pagina_inicial(g.usuario))
    form = EsqueciSenhaForm(prefix='esq')
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        usuario = UsuarioService.buscar_por_email(email)
        if usuario and VerificacaoService.segundos_para_reenviar('senha', email) == 0:
            codigo = VerificacaoService.gerar('senha', email)
            EmailService.enviar(email, 'SiteBio — código para criar uma nova senha',
                                mensagens_email.codigo_verificacao(usuario.nome, codigo, 'redefinir sua senha'))
        # Mensagem igual exista a conta ou não: não revela quais e-mails estão cadastrados.
        flash("Se este e-mail estiver cadastrado, enviamos um código de 6 números (vale 15 minutos). "
              "Olhe também a caixa de spam.", "info")
        return redirect(url_for('acesso.redefinir_senha', email=email))
    return render_template('auth/esqueci_senha.html', form=form)


@bp.route('/redefinir-senha', methods=['GET', 'POST'])
def redefinir_senha():
    if g.usuario:
        return redirect(pagina_inicial(g.usuario))
    form = RedefinirSenhaForm(prefix='red')
    if request.method == 'GET':
        form.email.data = request.args.get('email', '')
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        reg, erro = VerificacaoService.validar('senha', email, form.codigo.data)
        usuario = UsuarioService.buscar_por_email(email)
        if erro:
            form.codigo.errors = list(form.codigo.errors) + [erro]
        elif usuario is None:
            form.email.errors = list(form.email.errors) + ["E-mail não encontrado."]
        else:
            UsuarioService.atualizar(usuario.id, {'nome': usuario.nome, 'email': usuario.email,
                                                  'senha': form.senha.data})
            VerificacaoService.consumir(reg)
            flash("Senha alterada com sucesso! Entre com a nova senha.", "success")
            return redirect(url_for('acesso.auth'))
    return render_template('auth/redefinir_senha.html', form=form)
