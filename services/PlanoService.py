"""Mini plano de estudos semanal (só estudantes). Um modelo único para todos; quem tem mais
dúvidas em um tema recebe ênfase (tempo extra + reforço) nos blocos desse tema."""

MIN_BASE = 30          # minutos de leitura de cada bloco
MIN_REFORCO = 20       # minutos extras nos temas com mais dúvidas
MAX_TEMAS_ENFASE = 2

# (título do bloco, tema, rota da página fixa)
BLOCOS = {
    'celula': ('Célula e Microscópio', 'Célula', 'celula'),
    'teoria': ('Teoria Celular e Organelas', 'Célula', 'celula'),
    'citologia': ('Citologia', 'Citologia', 'citologia'),
    'dna': ('DNA e Cromossomos', 'DNA', 'dna'),
    'engrenagem': ('A Engrenagem da Vida', 'Metabolismo', 'cont'),
    'continuidade': ('A Continuidade da Vida', 'Metabolismo', 'cont'),
    'edsex': ('Educação Sexual', 'EducacaoSexual', 'ed_sex'),
    'manutencao': ('A Manutenção do Sistema', 'Metabolismo', 'manutencao'),
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


class PlanoService:
    def montar(self, duvidas, conteudos_publicados=()):
        """duvidas = saída de RespostaQuizService.duvidas_por_tema(). Devolve (dias, temas_enfase)."""
        enfase = [d['tema'] for d in duvidas if d['erros'] > 0][:MAX_TEMAS_ENFASE]
        dias = []
        for nome_dia, chaves in SEMANA:
            itens = []
            for chave in chaves:
                titulo, tema, rota = BLOCOS[chave]
                reforco = tema in enfase
                itens.append(dict(titulo=titulo, tema=tema, rota=rota, reforco=reforco,
                                  minutos=MIN_BASE + (MIN_REFORCO if reforco else 0)))
            dias.append(dict(dia=nome_dia, itens=itens, fechamento=None, extras=[]))

        # Fechamento do dia: mini-quiz do tema; no domingo, revisão geral + reforço dos temas em ênfase
        for d in dias[:-1]:
            d['fechamento'] = f"10 min: refazer o quiz de {d['itens'][0]['titulo']}"
        dom = dias[-1]
        dom['fechamento'] = '20 min: revisão geral da semana e um quiz completo'
        for tema in enfase:
            dom['extras'].append(tema)
        for c in conteudos_publicados:
            dom['itens'].append(dict(titulo=c.titulo, tema=c.tema, rota=None, conteudo_id=c.id,
                                     reforco=c.tema in enfase,
                                     minutos=MIN_BASE + (MIN_REFORCO if c.tema in enfase else 0)))
        return dias, enfase
