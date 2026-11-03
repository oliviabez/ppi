from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Optional, Regexp

# Validador de e-mail próprio (formato básico: algo@dominio.ext).
# Motivo: o validador Email() do WTForms exige o pacote "email-validator"; se ele não estiver
# instalado, o login/cadastro quebra com "Internal Server Error". Assim não há dependência extra.
Email = lambda: Regexp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', message='Informe um e-mail válido.')


class UsuarioForm(FlaskForm):
    """Cadastro (usar com prefix='cad')."""
    nome = StringField('Nome', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('E-mail', validators=[DataRequired(), Email(), Length(max=120)])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirmar_senha = PasswordField('Confirmar senha', validators=[
        DataRequired(), EqualTo('senha', message='As senhas não são iguais.')])
    perfil = SelectField('Perfil', choices=[('Estudante', 'Estudante'),
                                            ('Publico', 'Público Externo'),
                                            ('Admin', 'Administrador')])
    # Só é exigido quando o perfil escolhido é Administrador (a checagem é feita na rota).
    codigo_admin = StringField('Código de administrador', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Criar conta')


class LoginForm(FlaskForm):
    """Login (usar com prefix='login')."""
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
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
    submit = SubmitField('Salvar alterações')


class ExcluirContaForm(FlaskForm):
    """Exclusão da própria conta (usar com prefix='excluir')."""
    senha_atual = PasswordField('Digite sua senha para confirmar', validators=[DataRequired()])
    submit = SubmitField('Excluir minha conta')


class AcaoForm(FlaskForm):
    """Formulário vazio: serve só para proteger com token CSRF os botões de sair/excluir."""