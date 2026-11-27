from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Optional
from app.constantes import PERFIL_ESTUDANTE, PERFIL_PUBLICO, PERFIL_ADMIN
from app.forms.validators import Email


class UsuarioForm(FlaskForm):
    """Cadastro (usar com prefix='cad')."""
    nome = StringField('Nome', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('E-mail', validators=[DataRequired(), Email(), Length(max=120)])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirmar_senha = PasswordField('Confirmar senha', validators=[
        DataRequired(), EqualTo('senha', message='As senhas não são iguais.')])
    perfil = SelectField('Perfil', choices=[(PERFIL_ESTUDANTE, 'Estudante'),
                                            (PERFIL_PUBLICO, 'Público externo'),
                                            (PERFIL_ADMIN, 'Administrador')])
    # Só é exigido quando o perfil escolhido é Administrador (a checagem é feita no UsuarioService).
    codigo_admin = StringField('Código de administrador', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Criar conta')


class LoginForm(FlaskForm):
    """Login (usar com prefix='login')."""
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    # Só administradores precisam preencher (a checagem é feita na rota).
    codigo_admin = StringField('Código de administrador (só para administradores)',
                               validators=[Optional(), Length(max=100)])
    submit = SubmitField('Entrar')


class PerfilForm(FlaskForm):
    """Edição do próprio cadastro. Exige a senha atual para confirmar qualquer alteração."""
    nome = StringField('Nome', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('E-mail', validators=[DataRequired(), Email(), Length(max=120)])
    senha_nova = PasswordField('Nova senha (deixe em branco para manter)',
                               validators=[Optional(), Length(min=6)])
    confirmar_nova = PasswordField('Confirmar nova senha', validators=[
        EqualTo('senha_nova', message='As senhas não são iguais.')])
    senha_atual = PasswordField('Senha atual (para confirmar)', validators=[DataRequired()])
    # Só administradores: o código do .env é pedido para salvar alterações (a checagem é feita na rota).
    codigo_admin = StringField('Código de administrador', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Salvar alterações')


class ExcluirContaForm(FlaskForm):
    """Exclusão da própria conta (usar com prefix='excluir')."""
    senha_atual = PasswordField('Digite sua senha para confirmar', validators=[DataRequired()])
    submit = SubmitField('Excluir minha conta')


class AcaoForm(FlaskForm):
    """Formulário vazio: serve só para proteger com token CSRF os botões de sair/excluir."""