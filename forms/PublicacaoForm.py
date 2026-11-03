from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from app.constantes import TEMAS_CONTEUDO


class PublicacaoForm(FlaskForm):
    """Formulário do administrador para criar/editar conteúdos."""
    titulo = StringField('Título do Conteúdo', validators=[DataRequired(), Length(max=200)])
    tema = SelectField('Tema', choices=TEMAS_CONTEUDO)
    descricao = StringField('Descrição curta (opcional)', validators=[Optional(), Length(max=500)])
    texto = TextAreaField('Texto Explicativo Completo', validators=[DataRequired()])
    submit = SubmitField('Publicar Conteúdo')
