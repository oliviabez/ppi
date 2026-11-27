"""Filtros de template (Jinja) do SiteBio."""
import re
from flask import url_for
from app import app
from app.constantes import ROTULO_PERFIL, TEMAS_FEEDBACK
from app.services import filtro, imagem_texto
from app.utils import recente as _recente


@app.template_filter('data_br')
def data_br(valor):
    return valor.strftime('%d/%m/%Y %H:%M') if valor else ''


@app.template_filter('rotulo_perfil')
def rotulo_perfil(valor):
    return ROTULO_PERFIL.get(valor, valor)


@app.template_filter('censurar')
def censurar(valor):
    """Palavras obscenas aparecem rasuradas (ver services/filtro.py)."""
    return filtro.censurar(valor)


app.add_template_filter(_recente, 'recente')            # selo "Novo" (ver utils.recente)


@app.template_filter('titulo_quiz')
def titulo_quiz(titulo):
    """Tira marcações do tipo '(editável)' do título: elas só devem aparecer para administradores."""
    return re.sub(r'\s*\(\s*edit[aá]vel[^)]*\)', '', titulo or '', flags=re.I).strip()


@app.template_filter('rotulo_tema')
def rotulo_tema(valor):
    return dict(TEMAS_FEEDBACK).get(valor, valor)


@app.template_filter('texto_com_imagens')
def texto_com_imagens(texto, imagens):
    """Conteúdo publicado (texto puro) -> parágrafos + imagens nos pontos [imagem N]."""
    return imagem_texto.texto_com_imagens(texto, imagens)


@app.template_filter('html_com_imagens')
def html_com_imagens(html, imagens):
    """Seção de página fixa (HTML já limpo) -> imagens nos pontos [imagem N]."""
    return imagem_texto.html_com_imagens(html, imagens)


@app.template_filter('resumo')
def resumo(texto, tamanho=110):
    """Início do texto para cartões (sem as marcações de imagem)."""
    limpo = imagem_texto.sem_marcas(texto)
    return limpo[:tamanho] + ('…' if len(limpo) > tamanho else '')


@app.template_filter('duracao')
def duracao(minutos):
    """45 -> '45 min' | 90 -> '1 h 30 min' | 120 -> '2 h'."""
    horas, resto = divmod(int(minutos or 0), 60)
    if not horas:
        return f'{resto} min'
    return f'{horas} h' + (f' {resto} min' if resto else '')


@app.template_filter('texto_para_editor')
def texto_para_editor(texto, imagens):
    """Texto publicado -> conteúdo da caixa de edição (figuras no lugar de [imagem N])."""
    return imagem_texto.texto_para_editor(texto, imagens or [])


@app.template_filter('html_para_editor')
def html_para_editor(html, imagens):
    """Seção de página fixa -> conteúdo da caixa de edição (figuras no lugar de [imagem N])."""
    return imagem_texto.html_para_editor(html, imagens or [])


@app.template_filter('imagens_json')
def imagens_json(imagens):
    """Lista de imagens (na mesma ordem do servidor) para o JavaScript do editor."""
    return [{'id': i.id, 'url': url_for('static', filename='uploads/' + i.arquivo), 'legenda': i.legenda or ''}
            for i in imagens or []]
