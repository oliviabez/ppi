"""Edição do texto das páginas de conteúdo FIXAS (celula, citologia, dna, cont, ed_sex, manutencao).

O texto original continua nos templates. Quando o admin salva uma edição, ela vai para o banco e
passa a ser exibida no lugar do original. 'Restaurar original' apaga a edição."""
import json
import re
import textwrap
from datetime import datetime
from flask import current_app
from app.constantes import PAGINAS_FIXAS
from app.models.extras import PaginaEditada
from app.services.repositorio import Repositorio
from app.services.sanitizar import limpar_html

_repo = Repositorio(PaginaEditada, 'paginas_editadas', padroes={'data': datetime.now})
_ARTIGO = re.compile(r'<article class="content-block[^"]*">(.*?)</article>', re.S)
_TITULO = re.compile(r'<h3 class="section-title">(.*?)</h3>', re.S)
MAX_SECOES = 30


class PaginaService:
    def secoes_editadas(self, chave):
        """Lista [{'titulo','html'}] salva pelo admin, ou None se a página está no texto original."""
        reg = _repo.um(pagina=chave)
        if reg is None:
            return None
        try:
            return json.loads(reg.secoes)
        except ValueError:
            return None

    def secoes_originais(self, chave):
        """Lê as seções (cada <article>) do template original da página."""
        arquivo = {'ed_sex': 'ed.sex.html'}.get(chave, f'{chave}.html')
        env = current_app.jinja_env
        fonte = env.loader.get_source(env, arquivo)[0]
        secoes = []
        for corpo in _ARTIGO.findall(fonte):
            m = _TITULO.search(corpo)
            titulo = re.sub(r'<[^>]+>', '', m.group(1)).strip() if m else ''
            resto = corpo[m.end():] if m else corpo
            secoes.append({'titulo': titulo, 'html': textwrap.dedent(resto.strip('\n')).strip()})
        return secoes

    def secoes_para_editar(self, chave):
        return self.secoes_editadas(chave) or self.secoes_originais(chave)

    def salvar(self, chave, secoes):
        """secoes = [{'titulo','html'}]; o HTML é limpo antes de gravar."""
        limpas = [{'titulo': s['titulo'].strip()[:200], 'html': limpar_html(s['html'])} for s in secoes]
        texto = json.dumps(limpas, ensure_ascii=False)
        reg = _repo.um(pagina=chave)
        if reg is None:
            _repo.adicionar(pagina=chave, secoes=texto)
        else:
            reg.secoes, reg.data = texto, datetime.now()
            _repo.salvar()

    def restaurar(self, chave):
        _repo.excluir_onde(pagina=chave)

    @staticmethod
    def titulo(chave):
        return PAGINAS_FIXAS[chave][1]
