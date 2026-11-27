from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from app.constantes import TEMAS_CONTEUDO


class PublicacaoForm(FlaskForm):
    """Formulário do administrador para criar/editar conteúdos (título, tema e descrição)."""
    titulo = StringField('Título do Conteúdo', validators=[DataRequired(), Length(max=200)])
    tema = SelectField('Tema', choices=TEMAS_CONTEUDO)
    descricao = StringField('Descrição curta (opcional)', validators=[Optional(), Length(max=500)])
    # O texto é digitado em várias caixas (caixa_1, caixa_2...) e lido por ConteudoService.ler_caixas().
    submit = SubmitField('Publicar Conteúdo')
