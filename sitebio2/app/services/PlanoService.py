"""Plano de estudos semanal (só estudantes), com horários.

O estudante escolhe quanto tempo tem por dia e a hora em que começa. O plano divide EXATAMENTE esse tempo
entre os blocos do dia (temas com mais dúvidas ganham uma fatia maior, sem aumentar o total), reserva o
fechamento (refazer o quiz) e mostra o horário de início e fim de cada etapa.
"""
import re

OPCOES_MINUTOS = (30, 45, 60, 90, 120, 180)    # tempo disponível por dia
MINUTOS_PADRAO = 60
INICIO_PADRAO = '19:00'
MIN_ITEM = 10                  # nenhum bloco de leitura fica com menos que isso
MIN_REFORCO_QUIZ = 15          # quiz extra dos temas com mais dúvidas (domingo)
FECHAMENTO_DIA = 10            # refazer o quiz do dia
FECHAMENTO_DOMINGO = 20        # revisão geral da semana
PESO_REFORCO = 1.5             # no mesmo dia, o bloco de tema com dúvidas ganha 50% mais tempo
MAX_TEMAS_ENFASE = 2
MAX_PUBLICADOS = 3             # conteúdos publicados pelo admin incluídos no domingo (os mais recentes)

_HORA = re.compile(r'^([01]\d|2[0-3]):([0-5]\d)$')

# (título do bloco, tema, endpoint da página fixa)
BLOCOS = {
    'celula': ('Célula e Microscópio', 'Célula', 'conteudo.celula'),
    'teoria': ('Teoria Celular e Organelas', 'Célula', 'conteudo.celula'),
    'citologia': ('Citologia', 'Citologia', 'conteudo.citologia'),
    'dna': ('DNA e Cromossomos', 'DNA', 'conteudo.dna'),
    'engrenagem': ('A Engrenagem da Vida', 'Metabolismo', 'conteudo.cont'),
    'continuidade': ('A Continuidade da Vida', 'Metabolismo', 'conteudo.cont'),
    'edsex': ('Educação Sexual', 'EducacaoSexual', 'conteudo.ed_sex'),
    'manutencao': ('A Manutenção do Sistema', 'Metabolismo', 'conteudo.manutencao'),
}

# Modelo da semana (igual para todos os estudantes)
SEMANA = [
    ('Segunda', ['celula']),
    ('Terça', ['teoria']),
    ('Quarta', ['citologia']),
    ('Quinta', ['dna']),
    ('Sexta', ['engrenagem']),
    ('Sábado', ['continuidade', 'edsex']),
    ('Domingo', ['manutencao']),
]


def _distribuir(total, pesos):
    """Reparte 'total' minutos (múltiplo de 5) em partes de 5 min proporcionais aos pesos.
    Cada parte tem pelo menos MIN_ITEM e a soma dá exatamente 'total'."""
    unidades, minimo, soma = total // 5, MIN_ITEM // 5, sum(pesos)
    exatos = [unidades * p / soma for p in pesos]
    partes = [max(minimo, int(x)) for x in exatos]
    while sum(partes) < unidades:
        i = max(range(len(partes)), key=lambda k: exatos[k] - partes[k])
        partes[i] += 1
    while sum(partes) > unidades:
        i = min((k for k in range(len(partes)) if partes[k] > minimo), key=lambda k: exatos[k] - partes[k])
        partes[i] -= 1
    return [p * 5 for p in partes]


def _hora(minutos_do_dia):
    return f"{(minutos_do_dia // 60) % 24:02d}:{minutos_do_dia % 60:02d}"


class PlanoService:
    OPCOES_MINUTOS = OPCOES_MINUTOS

    @staticmethod
    def validar_parametros(minutos, inicio):
        """Aceita só valores conhecidos (o que vem da URL não é confiável)."""
        try:
            minutos = int(minutos)
        except (TypeError, ValueError):
            minutos = MINUTOS_PADRAO
        if minutos not in OPCOES_MINUTOS:
            minutos = MINUTOS_PADRAO
        if not _HORA.match(inicio or ''):
            inicio = INICIO_PADRAO
        return minutos, inicio

    @staticmethod
    def montar(duvidas, conteudos_publicados=(), minutos_dia=MINUTOS_PADRAO, inicio=INICIO_PADRAO):
        """duvidas = saída de RespostaQuizService.duvidas_por_tema().
        Devolve (dias, temas_enfase). Cada dia: {'dia', 'passos', 'total'}; cada passo tem 'tipo'
        ('estudo' | 'reforco' | 'fechamento'), 'inicio', 'fim' e 'minutos'."""
        enfase = [d['tema'] for d in duvidas if d['erros'] > 0][:MAX_TEMAS_ENFASE]
        h, m = (int(x) for x in inicio.split(':'))
        dias = []
        for posicao, (nome_dia, chaves) in enumerate(SEMANA):
            domingo = posicao == len(SEMANA) - 1
            base = []
            for chave in chaves:
                titulo, tema, rota = BLOCOS[chave]
                base.append(dict(titulo=titulo, tema=tema, rota=rota, conteudo_id=None, reforco=tema in enfase))
            publicados = []
            if domingo:
                publicados = [dict(titulo=c.titulo, tema=c.tema, rota=None, conteudo_id=c.id, reforco=c.tema in enfase)
                              for c in list(conteudos_publicados)[:MAX_PUBLICADOS]]
            extras = list(enfase) if domingo else []
            fechamento = FECHAMENTO_DOMINGO if domingo else FECHAMENTO_DIA

            # O dia tem SEMPRE o tempo escolhido: se não couber tudo, tira primeiro os conteúdos
            # publicados mais antigos e depois os quizzes de reforço (cada leitura precisa de MIN_ITEM).
            def sobra(n_itens, n_extras):
                return minutos_dia - fechamento - MIN_REFORCO_QUIZ * n_extras - MIN_ITEM * n_itens
            itens = base + publicados
            while len(itens) > len(base) and sobra(len(itens), len(extras)) < 0:
                itens.pop()
            while extras and sobra(len(itens), len(extras)) < 0:
                extras.pop()
            leitura = minutos_dia - fechamento - MIN_REFORCO_QUIZ * len(extras)
            pesos = [PESO_REFORCO if it['reforco'] else 1 for it in itens]
            duracoes = _distribuir(leitura, pesos)

            passos, relogio = [], h * 60 + m
            for it, duracao in zip(itens, duracoes):
                passos.append(dict(it, tipo='estudo', minutos=duracao,
                                   inicio=_hora(relogio), fim=_hora(relogio + duracao)))
                relogio += duracao
            for tema in extras:
                passos.append(dict(tipo='reforco', tema=tema, minutos=MIN_REFORCO_QUIZ,
                                   inicio=_hora(relogio), fim=_hora(relogio + MIN_REFORCO_QUIZ)))
                relogio += MIN_REFORCO_QUIZ
            temas = [] if domingo else list(dict.fromkeys(it['tema'] for it in itens))
            passos.append(dict(tipo='fechamento', temas=temas, minutos=fechamento,
                               inicio=_hora(relogio), fim=_hora(relogio + fechamento)))
            dias.append(dict(dia=nome_dia, passos=passos, total=sum(p['minutos'] for p in passos)))
        return dias, enfase