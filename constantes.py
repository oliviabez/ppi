"""Constantes compartilhadas (perfis, temas e tipos de envio)."""

PERFIL_ESTUDANTE = 'Estudante'
PERFIL_PUBLICO = 'Publico'
PERFIL_ADMIN = 'Admin'

ROTULO_PERFIL = {
    PERFIL_ESTUDANTE: 'Estudante',
    PERFIL_PUBLICO: 'Público externo',
    PERFIL_ADMIN: 'Administrador',
}

# Temas dos conteúdos publicados pelo administrador
TEMAS_CONTEUDO = [
    ('Célula', 'Célula e Microscópio'),
    ('Citologia', 'Citologia'),
    ('DNA', 'DNA e Cromossomos'),
    ('Metabolismo', 'Metabolismo e Continuidade'),
    ('EducacaoSexual', 'Educação Sexual'),
]

# Sobre o que o usuário está comentando / dando feedback
TEMAS_FEEDBACK = TEMAS_CONTEUDO + [('Quiz', 'Quiz'), ('Site', 'Site em geral')]

# Regra do documento do projeto:
#   Estudantes -> comentários e feedbacks | Público externo -> somente feedbacks
TIPOS_POR_PERFIL = {
    PERFIL_ESTUDANTE: [('Feedback', 'Feedback'), ('Comentario', 'Comentário / dúvida')],
    PERFIL_PUBLICO: [('Feedback', 'Feedback')],
}


# ─────────────────────────────────────────────────────────────────────────
# Páginas de conteúdo FIXAS do site: chave -> (nome da rota, título, tema usado no quiz/plano)
PAGINAS_FIXAS = {
    'celula': ('celula', 'Célula e Microscópio', 'Célula'),
    'citologia': ('citologia', 'Citologia', 'Citologia'),
    'dna': ('dna', 'DNA e Cromossomos', 'DNA'),
    'cont': ('cont', 'Engrenagem e Continuidade da Vida', 'Metabolismo'),
    'ed_sex': ('ed_sex', 'Educação Sexual', 'EducacaoSexual'),
    'manutencao': ('manutencao', 'Manutenção do Sistema', 'Metabolismo'),
}

# Tema de cada pergunta do quiz padrão (o que está fixo no código), para saber onde o aluno erra mais.
TEMA_PERGUNTA_FIXA = {'q1': 'Célula', 'q2': 'DNA', 'q3': 'DNA', 'q4': 'Citologia', 'q5': 'Metabolismo'}
QUIZ_PADRAO_TITULO = 'Biologia Celular'

# Rota da página fixa de cada tema (para linkar "estude este conteúdo")
ROTA_POR_TEMA = {'Célula': 'celula', 'Citologia': 'citologia', 'DNA': 'dna',
                 'Metabolismo': 'cont', 'EducacaoSexual': 'ed_sex'}

EXTENSOES_IMAGEM = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
