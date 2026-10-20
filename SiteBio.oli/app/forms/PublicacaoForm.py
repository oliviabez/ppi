from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired

class PublicacaoForm(FlaskForm):
    titulo = StringField('Título do Conteúdo', validators=[DataRequired()])
    tema = SelectField('Tema', choices=[('Célula', 'Célula e Microscópio'), ('Citologia', 'Citologia'), ('DNA', 'DNA e Cromossomos'), ('Metabolismo', 'Metabolismo e Continuidade'), ('EducacaoSexual', 'Educação Sexual')])
    conteudo = TextAreaField('Texto Explicativo Completo', validators=[DataRequired()])
    submit = SubmitField('Publicar Conteúdo')
