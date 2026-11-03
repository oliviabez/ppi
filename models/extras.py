"""Tabelas NOVAS (não alteram nenhuma tabela que já existia).

O db.create_all() só cria o que ainda não existe; por isso o banco atual continua igual e
estas tabelas aparecem sozinhas na próxima vez que o servidor subir.
"""
from datetime import datetime
from app import db


class ImagemConteudo(db.Model):
    """Imagem anexada a um conteúdo publicado (conteudo_id) OU a uma página fixa (pagina)."""
    __tablename__ = 'imagens_conteudo'

    id = db.Column(db.Integer, primary_key=True)
    conteudo_id = db.Column(db.Integer, db.ForeignKey('conteudos.id', ondelete='CASCADE'),
                            nullable=True)
    pagina = db.Column(db.String(30), nullable=True)      # celula | citologia | dna | cont | ed_sex | manutencao
    arquivo = db.Column(db.String(100), nullable=False)   # nome do arquivo em static/uploads/
    legenda = db.Column(db.String(200))
    data = db.Column(db.DateTime, default=datetime.now)


class RespostaComentario(db.Model):
    """Resposta de um administrador a uma dúvida (comentário) de estudante."""
    __tablename__ = 'respostas_comentario'

    id = db.Column(db.Integer, primary_key=True)
    comentario_id = db.Column(db.Integer, db.ForeignKey('comentarios.id', ondelete='CASCADE'),
                              nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='SET NULL'),
                         nullable=True)
    admin_nome = db.Column(db.String(100), nullable=False)
    texto = db.Column(db.String(1000), nullable=False)
    data = db.Column(db.DateTime, default=datetime.now)


class VerificacaoEmail(db.Model):
    """Códigos enviados por e-mail: confirmação de cadastro ('cadastro') e senha esquecida ('senha').

    ATENÇÃO: o código NUNCA é guardado puro, só o hash. Para 'cadastro' também ficam aqui os dados
    do cadastro pendente (a conta só é criada depois que o código é digitado).
    """
    __tablename__ = 'verificacoes_email'

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(120), nullable=False, index=True)
    codigo_hash = db.Column(db.String(64), nullable=False)
    expira = db.Column(db.DateTime, nullable=False)
    tentativas = db.Column(db.Integer, nullable=False, default=0)
    nome = db.Column(db.String(100))
    senha_hash = db.Column(db.String(200))
    perfil = db.Column(db.String(20))
    data = db.Column(db.DateTime, default=datetime.now)


class RespostaQuiz(db.Model):
    """Uma resposta dada em um quiz (só de estudantes) — base de 'meus erros' e do plano de estudos."""
    __tablename__ = 'respostas_quiz'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'),
                           nullable=False, index=True)
    resultado_id = db.Column(db.Integer, db.ForeignKey('resultados_quiz.id', ondelete='CASCADE'),
                             nullable=True)
    quiz_titulo = db.Column(db.String(200), nullable=False)
    tema = db.Column(db.String(50), nullable=False)
    enunciado = db.Column(db.Text, nullable=False)
    marcada = db.Column(db.String(1))
    marcada_texto = db.Column(db.String(200))
    correta = db.Column(db.String(1), nullable=False)
    correta_texto = db.Column(db.String(200))
    acertou = db.Column(db.Boolean, nullable=False, default=False)
    data = db.Column(db.DateTime, default=datetime.now)


class PaginaEditada(db.Model):
    """Texto editado pelo admin de uma página de conteúdo FIXA (celula, dna...).
    Enquanto não existir linha aqui, a página mostra o texto original do template."""
    __tablename__ = 'paginas_editadas'

    id = db.Column(db.Integer, primary_key=True)
    pagina = db.Column(db.String(30), unique=True, nullable=False)
    secoes = db.Column(db.Text, nullable=False)          # JSON: [{"titulo": "...", "html": "..."}]
    data = db.Column(db.DateTime, default=datetime.now)


class ConfigSite(db.Model):
    """Pequenas marcações do sistema (ex.: o quiz padrão já foi copiado para o banco?)."""
    __tablename__ = 'config_site'

    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(50), unique=True, nullable=False)
    valor = db.Column(db.String(200))
