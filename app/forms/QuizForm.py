from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField
from wtforms.validators import DataRequired

class QuizForm(FlaskForm):
    q1 = RadioField('1. Qual organela é responsável pela respiração celular?', choices=[('A', 'Lisossomo'), ('B', 'Mitocôndria'), ('C', 'Complexo de Golgi'), ('D', 'Ribossomo')], validators=[DataRequired()])
    q2 = RadioField('2. Quantas pontes de hidrogênio unem Citosina e Guanina?', choices=[('A', '2'), ('B', '3'), ('C', '4'), ('D', '1')], validators=[DataRequired()])
    q3 = RadioField('3. Quantos cromossomos tem cada gameta humano?', choices=[('A', '46'), ('B', '44'), ('C', '23'), ('D', '22')], validators=[DataRequired()])
    q4 = RadioField('4. Qual estrutura é exclusiva da célula vegetal?', choices=[('A', 'Lisossomo'), ('B', 'Mitocôndria'), ('C', 'Núcleo'), ('D', 'Parede celular')], validators=[DataRequired()])
    q5 = RadioField('5. Em que parte da célula ocorre a glicólise?', choices=[('A', 'Citoplasma (citosol)'), ('B', 'Matriz mitocondrial'), ('C', 'Núcleo'), ('D', 'Membrana interna da mitocôndria')], validators=[DataRequired()])
    submit = SubmitField('Enviar Respostas')
