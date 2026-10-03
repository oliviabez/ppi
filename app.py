from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "sitebio_secret_key"

# Banco de dados simulado em memória
users = []
comments = []
feedbacks = []
quizzes_results = []

# Módulos de conteúdo de Biologia baseados na ementa e PDF
MODULES = [
    {
        "id": "01",
        "slug": "celula-microscopio",
        "title": "Célula e Microscópio",
        "desc": "Tipos de microscópio, membrana, citoplasma, organelas, núcleo, ácidos nucleicos e cromossomos.",
        "tag": "PARTE I · CÉLULA E MICROSCÓPIO",
        "subtitle": "Do Microscópio ao Núcleo",
        "summary": "As ferramentas e as estruturas básicas para observar e entender a célula.",
        "template": "modules/celula_microscopio.html"
    },
    {
        "id": "02",
        "slug": "teoria-celular-organelas",
        "title": "Teoria Celular e Organelas",
        "desc": "Como a teoria foi construída e como RE, Golgi e lisossomos trabalham juntos.",
        "tag": "BIOLOGIA CELULAR PARTE 1",
        "subtitle": "Teoria Celular e Organelas",
        "summary": "Material de estudo organizado com carinho para o IFRN.",
        "template": "modules/teoria_celular.html"
    },
    {
        "id": "03",
        "slug": "citologia",
        "title": "Citologia",
        "desc": "Célula vegetal x animal, procariontes x eucariontes e transporte através da membrana.",
        "tag": "CITOLOGIA",
        "subtitle": "A ciência por trás da célula",
        "summary": "Da parede rígida das plantas às bombas iônicas da membrana animal.",
        "template": "modules/citologia.html"
    },
    {
        "id": "04",
        "slug": "dna-cromossomos",
        "title": "DNA e Cromossomos",
        "desc": "Nucleotídeos, dupla hélice, regra de Chargaff e empacotamento do DNA.",
        "tag": "MÓDULO 1 · BIOLOGIA MOLECULAR",
        "subtitle": "DNA e Cromossomos: a bioquímica da informação genética",
        "summary": "Estrutura molecular, nucleotídeos, dupla hélice e compactação cromossômica.",
        "template": "modules/dna_cromossomos.html"
    },
    {
        "id": "05",
        "slug": "metabolismo",
        "title": "A Engrenagem da Vida",
        "desc": "Metabolismo celular e alimentação saudável: da comida ao ATP.",
        "tag": "METABOLISMO CELULAR E ALIMENTAÇÃO",
        "subtitle": "A Engrenagem da Vida",
        "summary": "Como a célula transforma o que você come na energia necessária para ler o DNA e manter o corpo vivo.",
        "template": "modules/metabolismo.html"
    },
    {
        "id": "06",
        "slug": "continuidade",
        "title": "A Continuidade da Vida",
        "desc": "Energia, DNA e hormônios trabalhando juntos para gerar uma nova vida.",
        "tag": "REPRODUÇÃO E DIVISÃO CELULAR",
        "subtitle": "A Continuidade da Vida Humana",
        "summary": "Como energia, DNA e química corporal trabalham juntos para gerar uma nova vida.",
        "template": "modules/continuidade.html"
    },
    {
        "id": "07",
        "slug": "ed-sexual",
        "title": "Educação Sexual",
        "desc": "Puberdade, ciclo menstrual, prevenção, ISTs, consentimento e mitos e verdades.",
        "tag": "SAÚDE, CORPO E RESPEITO",
        "subtitle": "Educação Sexual: conhecer o corpo e cuidar de si",
        "summary": "Informação confiável, sem tabu, ligada ao que você já aprendeu sobre células, hormônios e DNA.",
        "template": "modules/ed_sexual.html"
    },
    {
        "id": "08",
        "slug": "manutencao",
        "title": "A Manutenção do Sistema",
        "desc": "Hábitos, exercício, sono e hidratação na bioquímica celular.",
        "tag": "CUIDADOS COM O CORPO",
        "subtitle": "A Manutenção do Sistema",
        "summary": "Hábitos diários, exercício físico, sono e hidratação na saúde e na bioquímica celular.",
        "template": "modules/manutencao.html"
    }
]

QUIZ_QUESTIONS = [
    {
        "id": 1,
        "question": "Qual organela é responsável pela respiração celular?",
        "options": ["Lisossomo", "Mitocôndria", "Complexo de Golgi", "Ribossomo"],
        "answer": "B"
    },
    {
        "id": 2,
        "question": "Quantas pontes de hidrogênio unem Citosina e Guanina?",
        "options": ["2 pontes", "3 pontes", "4 pontes", "1 ponte"],
        "answer": "B"
    },
    {
        "id": 3,
        "question": "Quantos cromossomos tem cada gameta humano?",
        "options": ["46", "44", "23", "22"],
        "answer": "C"
    },
    {
        "id": 4,
        "question": "Qual estrutura é exclusiva da célula vegetal?",
        "options": ["Lisossomo", "Mitocôndria", "Núcleo", "Parede celular"],
        "answer": "D"
    },
    {
        "id": 5,
        "question": "Em que parte da célula ocorre a glicólise?",
        "options": ["Citoplasma (citosol)", "Matriz mitocondrial", "Núcleo", "Membrana interna da mitocôndria"],
        "answer": "A"
    }
]

@app.route("/")
def index():
    query = request.args.get("q", "")
    filtered_modules = MODULES
    if query:
        filtered_modules = [m for m in MODULES if query.lower() in m["title"].lower() or query.lower() in m["desc"].lower()]
    return render_template("index.html", modules=filtered_modules, query=query)

@app.route("/modulo/<slug>", methods=["GET", "POST"])
def modulo_detail(slug):
    mod = next((m for m in MODULES if m["slug"] == slug), None)
    if not mod:
        flash("Módulo não encontrado.", "warning")
        return redirect(url_for("index"))
    
    if request.method == "POST":
        author = request.form.get("author", "Anônimo")
        text = request.form.get("text")
        if text:
            comments.append({"module": slug, "author": author, "text": text})
            flash("Comentário publicado com sucesso!", "success")
        return redirect(url_for("modulo_detail", slug=slug))
        
    mod_comments = [c for c in comments if c["module"] == slug]
    return render_template("modulo_detail.html", module=mod, comments=mod_comments)

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    score = None
    total = len(QUIZ_QUESTIONS)
    if request.method == "POST":
        hits = 0
        user_answers = {}
        for q in QUIZ_QUESTIONS:
            ans = request.form.get(f"q_{q['id']}")
            user_answers[q['id']] = ans
            if ans == q["answer"]:
                hits += 1
        score = {"hits": hits, "total": total, "percent": int((hits/total)*100)}
        quizzes_results.append(score)
    return render_template("quiz.html", questions=QUIZ_QUESTIONS, score=score)

@app.route("/auth", methods=["GET", "POST"])
def auth():
    if request.method == "POST":
        action = request.form.get("action")
        email = request.form.get("email")
        password = request.form.get("password")
        
        if action == "register":
            name = request.form.get("name")
            role = request.form.get("role")
            users.append({"name": name, "email": email, "role": role})
            flash(f"Conta criada com sucesso para {name}!", "success")
        else:
            flash(f"Bem-vindo de volta! ({email})", "info")
        return redirect(url_for("index"))
        
    return render_template("auth.html")

@app.route("/feedback", methods=["POST"])
def feedback():
    content = request.form.get("feedback_text")
    if content:
        feedbacks.append(content)
        flash("Obrigado pelo seu feedback!", "success")
    return redirect(request.referrer or url_for("index"))

@app.route("/admin")
def admin():
    return render_template("admin.html", users=users, feedbacks=feedbacks, results=quizzes_results)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
