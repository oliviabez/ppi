"""Limpa o HTML digitado pelo admin ao editar um conteúdo: mantém só marcações seguras de texto,
tabelas e listas; remove scripts, iframes, eventos (onclick...) e links perigosos."""
import re
from html import escape
from html.parser import HTMLParser

TAGS = {'p', 'br', 'strong', 'b', 'em', 'i', 'u', 'small', 'sup', 'sub', 'span', 'div', 'ul', 'ol', 'li',
        'h3', 'h4', 'h5', 'a', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'blockquote', 'hr',
        'figure', 'figcaption', 'img'}
VAZIAS = {'br', 'hr', 'img'}
DESCARTAR_CONTEUDO = {'script', 'style', 'iframe', 'object', 'embed', 'noscript', 'template'}
ATRIBUTOS = {'a': {'href'}, 'img': {'src', 'alt'}, 'td': {'colspan', 'rowspan'}, 'th': {'colspan', 'rowspan'}}
GLOBAIS = {'class', 'style'}
URL_OK = re.compile(r'^(https?://|mailto:|/|#)', re.I)


def _valor_ok(nome, valor, tag):
    if nome == 'class':
        return re.fullmatch(r'[\w\s-]*', valor) is not None
    if nome == 'style':
        return not re.search(r'url\s*\(|expression|javascript|@import|behavior', valor, re.I)
    if nome in ('href', 'src'):
        return bool(URL_OK.match(valor.strip()))
    return True


class _Limpador(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.saida, self.abertas, self.ignorando = [], [], 0

    def handle_starttag(self, tag, attrs):
        if tag in DESCARTAR_CONTEUDO:
            self.ignorando += 1
            return
        if self.ignorando or tag not in TAGS:
            return
        partes = []
        for nome, valor in attrs:
            nome, valor = (nome or '').lower(), valor or ''
            if (nome in GLOBAIS or nome in ATRIBUTOS.get(tag, ())) and _valor_ok(nome, valor, tag):
                partes.append(f'{nome}="{escape(valor, quote=True)}"')
        if tag == 'a':
            partes.append('rel="noopener noreferrer"')
        self.saida.append(f"<{tag}{' ' + ' '.join(partes) if partes else ''}>")
        if tag not in VAZIAS:
            self.abertas.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VAZIAS and tag in TAGS and not self.ignorando and self.abertas and self.abertas[-1] == tag:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in DESCARTAR_CONTEUDO:
            self.ignorando = max(0, self.ignorando - 1)
            return
        if self.ignorando or tag not in TAGS or tag in VAZIAS or tag not in self.abertas:
            return
        while self.abertas:                 # fecha o que ficou aberto no meio
            topo = self.abertas.pop()
            self.saida.append(f'</{topo}>')
            if topo == tag:
                break

    def handle_data(self, data):
        if not self.ignorando:
            self.saida.append(escape(data, quote=False))

    def handle_entityref(self, name):
        if not self.ignorando and re.fullmatch(r'\w+', name):
            self.saida.append(f'&{name};')

    def handle_charref(self, name):
        if not self.ignorando and re.fullmatch(r'#?\w+', name):
            self.saida.append(f'&#{name};')


def limpar_html(texto):
    p = _Limpador()
    p.feed(texto or '')
    p.close()
    p.saida.extend(f'</{t}>' for t in reversed(p.abertas))
    return ''.join(p.saida).strip()
