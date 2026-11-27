"""Imagens no meio do texto.

O administrador escreve [imagem 1], [imagem 2]... no texto e a imagem aparece naquele ponto
(o número é a ordem da imagem na lista do conteúdo/página). As imagens que não forem citadas
no texto aparecem no final, como antes.
"""
import re
from flask import url_for
from markupsafe import Markup

TOKEN = re.compile(r'\[\s*imagem\s+(\d+)\s*\]', re.I)
_PARAGRAFO_SO_COM_TOKEN = re.compile(r'<p[^>]*>\s*\[\s*imagem\s+(\d+)\s*\]\s*</p>', re.I)
_BLOCOS = re.compile(r'\n\s*\n')


def marca(numero):
    """Texto que o admin escreve para posicionar a imagem."""
    return f'[imagem {numero}]'


def numeros_usados(textos):
    """Números das imagens citadas em uma lista de textos."""
    return {int(n) for texto in textos for n in TOKEN.findall(texto or '')}


def ao_remover(texto, numero):
    """Quando a imagem 'numero' é removida: apaga a marcação dela e as imagens seguintes
    sobem um número (a [imagem 3] vira [imagem 2]), para o texto continuar certo sozinho."""
    def troca(m):
        n = int(m.group(1))
        return '' if n == numero else (marca(n - 1) if n > numero else m.group(0))
    limpo = TOKEN.sub(troca, texto or '')
    return re.sub(r'<p[^>]*>\s*</p>', '', limpo)          # parágrafo que ficou vazio (páginas fixas)


def livres(imagens, textos):
    """Imagens que NÃO foram citadas no texto (vão para o final)."""
    usados = numeros_usados(textos)
    return [img for n, img in enumerate(imagens, start=1) if n not in usados]


def sem_marcas(texto):
    """Texto sem as marcações [imagem N] (para prévias)."""
    return re.sub(r'\s{2,}', ' ', TOKEN.sub('', texto or '')).strip()


def figura(img):
    """HTML centralizado de uma imagem, com legenda opcional."""
    legenda = (Markup('<figcaption class="small mt-1"><em>%s</em></figcaption>') % img.legenda
               if img.legenda else '')
    return Markup('<figure class="figura-conteudo"><img class="img-fluid rounded" src="%s" alt="%s" '
                  'loading="lazy">%s</figure>') % (url_for('static', filename='uploads/' + img.arquivo),
                                                    img.legenda or 'Imagem do conteúdo', legenda)


def figuras(imagens):
    return Markup('').join(figura(img) for img in imagens)


def _paragrafo(texto):
    return Markup('<p>%s</p>') % Markup('<br>\n').join(Markup.escape(linha) for linha in texto.split('\n'))


def texto_com_imagens(texto, imagens):
    """Texto puro (conteúdos publicados) -> HTML seguro com parágrafos e as imagens nos lugares marcados."""
    saida = []
    for bloco in _BLOCOS.split(texto or ''):
        pos = 0
        for m in TOKEN.finditer(bloco):
            antes = bloco[pos:m.start()].strip()
            if antes:
                saida.append(_paragrafo(antes))
            n = int(m.group(1))
            if 1 <= n <= len(imagens):
                saida.append(figura(imagens[n - 1]))
            pos = m.end()
        resto = bloco[pos:].strip()
        if resto:
            saida.append(_paragrafo(resto))
    return Markup('').join(saida)


def html_com_imagens(html, imagens):
    """HTML das páginas fixas (já limpo pelo sanitizar) -> troca [imagem N] pela figura."""
    def troca(m):
        n = int(m.group(1))
        return str(figura(imagens[n - 1])) if 1 <= n <= len(imagens) else ''
    html = _PARAGRAFO_SO_COM_TOKEN.sub(troca, html or '')
    return Markup(TOKEN.sub(troca, html))


# ── Editor visual do administrador: a imagem aparece de verdade dentro da caixa de edição ──
def figura_editor(img):
    """Imagem como aparece NA CAIXA DE EDIÇÃO (o administrador vê a figura, não um código).
    Na hora de salvar, o JavaScript troca a figura de volta por [imagem N]."""
    legenda = (Markup('<figcaption>%s</figcaption>') % img.legenda) if img.legenda else Markup('')
    return Markup('<figure class="figura-editor" contenteditable="false" data-img="%s">'
                  '<img src="%s" alt="%s" draggable="false">%s'
                  '<button type="button" class="figura-tirar" title="Tirar a imagem do texto">&times;</button>'
                  '</figure>') % (img.id, url_for('static', filename='uploads/' + img.arquivo),
                                  img.legenda or 'Imagem', legenda)


def texto_para_editor(texto, imagens):
    """Conteúdo publicado (texto puro) -> HTML da caixa de edição: parágrafos + figuras."""
    saida = []
    for bloco in _BLOCOS.split(texto or ''):
        pos = 0
        for m in TOKEN.finditer(bloco):
            antes = bloco[pos:m.start()].strip()
            if antes:
                saida.append(_paragrafo(antes))
            n = int(m.group(1))
            if 1 <= n <= len(imagens):
                saida.append(figura_editor(imagens[n - 1]))
            pos = m.end()
        resto = bloco[pos:].strip()
        if resto:
            saida.append(_paragrafo(resto))
    return Markup('').join(saida) or Markup('<p><br></p>')


def html_para_editor(html, imagens):
    """Seção de página fixa (HTML) -> HTML da caixa de edição. Passa pela mesma limpeza do salvamento."""
    from app.services.sanitizar import limpar_html
    html = limpar_html(html)

    def troca(m):
        n = int(m.group(1))
        return str(figura_editor(imagens[n - 1])) if 1 <= n <= len(imagens) else ''
    html = _PARAGRAFO_SO_COM_TOKEN.sub(troca, html)
    return Markup(TOKEN.sub(troca, html) or '<p><br></p>')
