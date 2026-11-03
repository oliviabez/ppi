from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
from app.constantes import TEMAS_FEEDBACK


class ComentarioForm(FlaskForm):
    # As opções de 'tipo' dependem do perfil e são definidas na rota (estudante: feedback e
    # comentário; público externo: só feedback).
    tipo = SelectField('Tipo', choices=[('Feedback', 'Feedback')])
    tema = SelectField('Sobre qual assunto?', choices=TEMAS_FEEDBACK)
    texto = TextAreaField('Sua mensagem', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Enviar')
