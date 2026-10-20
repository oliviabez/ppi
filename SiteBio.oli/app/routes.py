from flask import render_template, request, redirect, url_for, flash
from app import app
from app.forms import UsuarioForm, LoginForm, ComentarioForm, PublicacaoForm, QuizForm

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/celula')
def celula():
    return render_template('celula.html')

@app.route('/citologia')
def citologia():
    return render_template('citologia.html')

@app.route('/dna')
def dna():
    return render_template('dna.html')

@app.route('/continuidade')
def cont():
    return render_template('cont.html')

@app.route('/educacao-sexual')
def ed_sex():
    return render_template('ed.sex.html')

@app.route('/manutencao')
def manutencao():
    return render_template('manutencao.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    form = QuizForm()
    resultado = None
    if form.validate_on_submit():
        acertos = 0
        if form.q1.data == 'B': acertos += 1
        if form.q2.data == 'B': acertos += 1
        if form.q3.data == 'C': acertos += 1
        if form.q4.data == 'D': acertos += 1
        if form.q5.data == 'A': acertos += 1
        resultado = f"Você acertou {acertos} de 5 perguntas!"
    return render_template('quiz.html', form=form, resultado=resultado)

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    login_form = LoginForm()
    usuario_form = UsuarioForm()
    return render_template('auth.html', login_form=login_form, usuario_form=usuario_form)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    pub_form = PublicacaoForm()
    return render_template('admin.html', pub_form=pub_form)
