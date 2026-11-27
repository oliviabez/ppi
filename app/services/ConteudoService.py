import re
from app import db
from app.constantes import PAGINAS_FIXAS
from app.models.conteudo import Conteudo
from app.services.imagem_texto import ao_remover

MAX_CAIXAS = 30
MAX_TEXTO = 30000
_BLOCOS = re.compile(r'\n\s*\n')


class ConteudoService:
    """Conteúdos educativos publicados pelo administrador."""

    @staticmethod
    def adicionar(dados, autor=None):
        """autor = usuário (admin) que está publicando."""
        novo = Conteudo(titulo=dados["titulo"].strip(), tema=dados["tema"],
                        descricao=(dados.get("descricao") or "").strip() or None,
                        texto=dados["texto"],
                        autor_id=autor.id if autor else None,
                        autor_nome=autor.nome if autor else None)
        db.session.add(novo)
        db.session.commit()
        return novo

    @staticmethod
    def listar_todos():
        return Conteudo.query.order_by(Conteudo.data_criacao.desc(), Conteudo.id.desc()).all()

    @staticmethod
    def buscar(conteudo_id):
        return db.session.get(Conteudo, conteudo_id)

    @classmethod
    def atualizar(cls, conteudo_id, dados):
        conteudo = cls.buscar(conteudo_id)
        if conteudo is None:
            return None
        conteudo.titulo = dados["titulo"].strip()
        conteudo.tema = dados["tema"]
        conteudo.descricao = (dados.get("descricao") or "").strip() or None
        conteudo.texto = dados["texto"]
        db.session.commit()
        return conteudo

    @classmethod
    def ajustar_marcas(cls, conteudo_id, numero_removido):
        """Depois de remover uma imagem: tira a marcação dela do texto e renumera as seguintes."""
        conteudo = cls.buscar(conteudo_id)
        if conteudo is not None:
            conteudo.texto = ao_remover(conteudo.texto, numero_removido)
            db.session.commit()

    @classmethod
    def excluir(cls, conteudo_id):
        conteudo = cls.buscar(conteudo_id)
        if conteudo is None:
            return False
        db.session.delete(conteudo)
        db.session.commit()
        return True

    @classmethod
    def paginas_do_tema(cls, tema):
        """Páginas de conteúdo fixas + conteúdos publicados que pertencem a um tema."""
        return ([(rota, titulo) for rota, titulo, t in PAGINAS_FIXAS.values() if t == tema],
                [c for c in cls.listar_todos() if c.tema == tema])

    @staticmethod
    def ler_texto(form):
        """Texto único enviado pelo editor visual (campo 'texto'): parágrafos separados por linha em branco."""
        texto = (form.get('texto') or '').replace('\r\n', '\n').replace('\r', '\n')
        return re.sub(r'\n{3,}', '\n\n', texto).strip()[:MAX_TEXTO]

    # ── (antigo) caixas de texto do formulário (cada caixa vira um bloco; blocos são separados por linha em branco) ──
    @staticmethod
    def ler_caixas(form):
        """Lê as caixas (caixa_1, caixa_2...) de um formulário. Caixas vazias são ignoradas."""
        total = min(form.get('total_caixas', type=int) or 0, MAX_CAIXAS)
        caixas = (form.get(f'caixa_{i}', '').strip() for i in range(1, total + 1))
        return [c for c in caixas if c]

    @staticmethod
    def juntar_caixas(caixas):
        return '\n\n'.join(caixas)

    @staticmethod
    def caixas_do_texto(texto):
        """Divide o texto salvo em caixas para a edição (uma caixa por bloco)."""
        return [b.strip() for b in _BLOCOS.split(texto or '') if b.strip()] or ['']
