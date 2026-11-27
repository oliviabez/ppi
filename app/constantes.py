"""Constantes compartilhadas (perfis, temas e tipos de envio)."""

PERFIL_ESTUDANTE = 'Estudante'
PERFIL_PUBLICO = 'Publico'
PERFIL_ADMIN = 'Admin'

# Tipos de mensagem enviada em Feedback e Comentários
TIPO_FEEDBACK = 'Feedback'
TIPO_COMENTARIO = 'Comentario'

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
    PERFIL_ESTUDANTE: [(TIPO_FEEDBACK, 'Feedback'), (TIPO_COMENTARIO, 'Comentário / dúvida')],
    PERFIL_PUBLICO: [(TIPO_FEEDBACK, 'Feedback')],
}


# ─────────────────────────────────────────────────────────────────────────
# Páginas de conteúdo FIXAS do site: chave -> (endpoint da rota, título, tema usado no quiz/plano)
PAGINAS_FIXAS = {
    'celula': ('conteudo.celula', 'Célula e Microscópio', 'Célula'),
    'citologia': ('conteudo.citologia', 'Citologia', 'Citologia'),
    'dna': ('conteudo.dna', 'DNA e Cromossomos', 'DNA'),
    'cont': ('conteudo.cont', 'Engrenagem e Continuidade da Vida', 'Metabolismo'),
    'ed_sex': ('conteudo.ed_sex', 'Educação Sexual', 'EducacaoSexual'),
    'manutencao': ('conteudo.manutencao', 'Manutenção do Sistema', 'Metabolismo'),
}

# Itens do menu "Conteúdos" (endpoint, nome curto). Usado em templates/shared/base.html.
MENU_CONTEUDOS = [
    ('conteudo.celula', 'Célula'),
    ('conteudo.citologia', 'Citologia'),
    ('conteudo.dna', 'DNA'),
    ('conteudo.cont', 'Engrenagem e Continuidade'),
    ('conteudo.ed_sex', 'Educação Sexual'),
    ('conteudo.manutencao', 'Manutenção do Sistema'),
]

QUIZ_PADRAO_TITULO = 'Biologia Celular'

# Rota da página fixa de cada tema (para linkar "estude este conteúdo")
ROTA_POR_TEMA = {'Célula': 'conteudo.celula', 'Citologia': 'conteudo.citologia', 'DNA': 'conteudo.dna',
                 'Metabolismo': 'conteudo.cont', 'EducacaoSexual': 'conteudo.ed_sex'}

EXTENSOES_IMAGEM = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
