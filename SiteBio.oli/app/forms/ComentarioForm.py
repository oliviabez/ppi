from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class ComentarioForm(FlaskForm):
    texto = TextAreaField('Seu comentário / Dúvida', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Enviar Feedback')
