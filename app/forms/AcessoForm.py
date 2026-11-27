from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Optional
from app.forms.validators import Email, Codigo


class EsqueciSenhaForm(FlaskForm):
    email = StringField('E-mail cadastrado', validators=[DataRequired(), Email(), Length(max=120)])
    submit = SubmitField('Enviar código')


class ConfirmarCadastroForm(FlaskForm):
    """Passo 2 do cadastro: o código que chegou no e-mail (prova que o e-mail existe)."""
    email = StringField('E-mail', validators=[DataRequired(), Email(), Length(max=120)])
    codigo = StringField('Código recebido por e-mail', validators=[DataRequired(), Codigo()])
    submit = SubmitField('Confirmar e criar conta')


class RedefinirSenhaForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email(), Length(max=120)])
    codigo = StringField('Código recebido por e-mail', validators=[DataRequired(), Codigo()])
    senha = PasswordField('Nova senha', validators=[DataRequired(), Length(min=6)])
    confirmar = PasswordField('Confirmar nova senha', validators=[
        DataRequired(), EqualTo('senha', message='As senhas não são iguais.')])
    submit = SubmitField('Redefinir senha')


class RespostaForm(FlaskForm):
    """Resposta do administrador a uma dúvida de estudante."""
    texto = TextAreaField('Sua resposta', validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField('Enviar resposta (e avisar por e-mail)')


class ContatoAdminForm(FlaskForm):
    """Estudante escreve para o e-mail de um administrador (fora do site)."""
    admin_id = SelectField('Para qual administrador?', coerce=int, validators=[DataRequired()])
    assunto = StringField('Assunto', validators=[DataRequired(), Length(max=120)])
    mensagem = TextAreaField('Mensagem', validators=[DataRequired(), Length(max=2000)])
    submit = SubmitField('Enviar por e-mail')
