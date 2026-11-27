"""Edição do texto das páginas de conteúdo FIXAS (celula, citologia, dna, cont, ed_sex, manutencao).

O texto original continua nos templates. Quando o admin salva uma edição, ela vai para o banco e
passa a ser exibida no lugar do original. 'Restaurar original' apaga a edição."""
import json
import re
import textwrap
from datetime import datetime
from flask import current_app
from app.models.pagina_editada import PaginaEditada
from app.services.DBRepository import DBRepository
from app.services.sanitizar import limpar_html
from app.services.imagem_texto import ao_remover

_repo = DBRepository(PaginaEditada)
_ARTIGO = re.compile(r'<article class="content-block[^"]*">(.*?)</article>', re.S)
_TITULO = re.compile(r'<h3 class="section-title">(.*?)</h3>', re.S)
MAX_SECOES = 30
MAX_SECOES_FORM = 40      # limite de blocos lidos de um formulário


class PaginaService:
    @staticmethod
    def secoes_editadas(chave):
        """Lista [{'titulo','html'}] salva pelo admin, ou None se a página está no texto original."""
        reg = _repo.um(pagina=chave)
        if reg is None:
            return None
        try:
            return json.loads(reg.secoes)
        except ValueError:
            return None

    @staticmethod
    def secoes_originais(chave):
        """Lê as seções (cada <article>) do template original da página."""
        arquivo = f'conteudo/{chave}.html'
        env = current_app.jinja_env
        fonte = env.loader.get_source(env, arquivo)[0]
        secoes = []
        for corpo in _ARTIGO.findall(fonte):
            m = _TITULO.search(corpo)
            titulo = re.sub(r'<[^>]+>', '', m.group(1)).strip() if m else ''
            resto = corpo[m.end():] if m else corpo
            secoes.append({'titulo': titulo, 'html': textwrap.dedent(resto.strip('\n')).strip()})
        return secoes

    @staticmethod
    def ler_secoes(form):
        """Lê as seções de um formulário (request.form): u<N>_titulo / u<N>_html."""
        secoes = []
        total = min(form.get('total', type=int) or 0, MAX_SECOES_FORM)
        for i in range(1, total + 1):
            if f'u{i}_titulo' not in form:              # seção removida na tela
                continue
            titulo = form.get(f'u{i}_titulo', '').strip()
            html = form.get(f'u{i}_html', '').strip()
            if titulo or html:
                secoes.append({'titulo': titulo, 'html': html})
        return secoes

    @classmethod
    def secoes_para_editar(cls, chave):
        return cls.secoes_editadas(chave) or cls.secoes_originais(chave)

    @staticmethod
    def salvar(chave, secoes):
        """secoes = [{'titulo','html'}]; o HTML é limpo antes de gravar."""
        limpas = [{'titulo': s['titulo'].strip()[:200], 'html': limpar_html(s['html'])} for s in secoes]
        texto = json.dumps(limpas, ensure_ascii=False)
        reg = _repo.um(pagina=chave)
        if reg is None:
            _repo.adicionar(pagina=chave, secoes=texto)
        else:
            reg.secoes, reg.data = texto, datetime.now()
            _repo.salvar()

    @classmethod
    def ajustar_marcas(cls, chave, numero_removido):
        """Depois de remover uma imagem da página: tira a marcação dela e renumera as seguintes."""
        secoes = cls.secoes_editadas(chave)
        if secoes:
            for secao in secoes:
                secao['html'] = ao_remover(secao['html'], numero_removido)
            reg = _repo.um(pagina=chave)
            reg.secoes = json.dumps(secoes, ensure_ascii=False)
            _repo.salvar()

    @staticmethod
    def restaurar(chave):
        _repo.excluir_onde(pagina=chave)
