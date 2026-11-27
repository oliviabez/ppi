"""Quizzes criados pelo administrador (um por conteúdo/tema), mesma estrutura do quiz padrão:
perguntas de múltipla escolha com 4 alternativas (A–D) e uma resposta correta."""
import re
from app.constantes import QUIZ_PADRAO_TITULO, TEMAS_CONTEUDO
from app.forms.QuizForm import QuizForm
from app.models.config_site import ConfigSite
from app.models.quiz import Quiz, Pergunta
from app.services.DBRepository import DBRepository

_quizzes = DBRepository(Quiz)
_perguntas = DBRepository(Pergunta)
_config = DBRepository(ConfigSite)

LETRAS = ('A', 'B', 'C', 'D')
CAMPOS_TEXTO = ('opcao_a', 'opcao_b', 'opcao_c', 'opcao_d')
MAX_PERGUNTAS_FORM = 40
PERGUNTAS_EM_BRANCO = 5          # mesma estrutura do quiz padrão: 5 perguntas

# Gabarito do quiz padrão (as perguntas e alternativas estão em forms/QuizForm.py)
GABARITO_PADRAO = {'q1': 'B', 'q2': 'B', 'q3': 'C', 'q4': 'D', 'q5': 'A'}


class QuizService:
    @staticmethod
    def listar(tema=None):
        return _quizzes.listar(ordenar='id', **({'tema': tema} if tema else {}))

    @staticmethod
    def buscar(quiz_id):
        return _quizzes.buscar(quiz_id)

    @staticmethod
    def perguntas_do_quiz(quiz_id):
        return _perguntas.listar(ordenar='id', quiz_id=quiz_id)

    @staticmethod
    def titulo_existe(titulo, ignorar_id=None):
        return any(q.titulo.strip().lower() == titulo.strip().lower() and q.id != ignorar_id
                   for q in _quizzes.listar())

    @staticmethod
    def _dados_pergunta(d):
        return dict(enunciado=d['enunciado'].strip(), opcao_a=d['opcao_a'].strip(),
                    opcao_b=d['opcao_b'].strip(), opcao_c=d['opcao_c'].strip(),
                    opcao_d=d['opcao_d'].strip(), resposta_correta=d['resposta_correta'])

    @classmethod
    def criar(cls, titulo, tema, perguntas):
        quiz = _quizzes.adicionar(titulo=titulo.strip(), tema=tema)
        for p in perguntas:
            _perguntas.adicionar(quiz_id=quiz.id, **cls._dados_pergunta(p))
        return quiz

    @classmethod
    def atualizar(cls, quiz, titulo, tema, perguntas):
        """Perguntas com 'id' são atualizadas; sem 'id' são criadas; as que sumiram são removidas."""
        quiz.titulo, quiz.tema = titulo.strip(), tema
        _quizzes.salvar()
        existentes = {p.id: p for p in cls.perguntas_do_quiz(quiz.id)}
        mantidos = set()
        for p in perguntas:
            dados = cls._dados_pergunta(p)
            if p.get('id') in existentes:
                alvo = existentes[p['id']]
                for campo, valor in dados.items():
                    setattr(alvo, campo, valor)
                mantidos.add(p['id'])
            else:
                _perguntas.adicionar(quiz_id=quiz.id, **dados)
        for pid, alvo in existentes.items():
            if pid not in mantidos:
                _perguntas.excluir(alvo)
        _perguntas.salvar()

    @staticmethod
    def excluir(quiz):
        _perguntas.excluir_onde(quiz_id=quiz.id)
        _quizzes.excluir(quiz)

    @classmethod
    def corrigir(cls, quiz, respostas):
        """respostas = {pergunta.id: 'A'..'D'}. Devolve (acertos, detalhes, faltando)."""
        detalhes, acertos, faltando = [], 0, []
        for n, p in enumerate(cls.perguntas_do_quiz(quiz.id), start=1):
            textos = {'A': p.opcao_a, 'B': p.opcao_b, 'C': p.opcao_c, 'D': p.opcao_d}
            marcada = respostas.get(p.id)
            if marcada not in LETRAS:
                faltando.append(n)
                continue
            ok = marcada == p.resposta_correta
            acertos += ok
            detalhes.append(dict(ref=f'p{p.id}', numero=n, enunciado=p.enunciado, marcada=marcada,
                                 marcada_texto=textos[marcada], correta=p.resposta_correta,
                                 correta_texto=textos[p.resposta_correta], acertou=ok, tema=quiz.tema))
        return acertos, detalhes, faltando

    # ── quiz padrão (antes fixo no código): vira um quiz comum, editável e que pode ser apagado ──
    @classmethod
    def garantir_padrao(cls, titulo, tema, perguntas):
        """Grava o quiz padrão no banco, se ainda não foi gravado (ver garantir_quiz_padrao)."""
        if _config.um(chave='quiz_padrao_importado'):
            return
        if not cls.titulo_existe(titulo):
            cls.criar(titulo, tema, perguntas)
        _config.adicionar(chave='quiz_padrao_importado', valor='1')

    @classmethod
    def garantir_quiz_padrao(cls):
        """O quiz padrão (antes fixo no código) é copiado UMA vez para o banco, e a partir daí é um
        quiz comum: o admin pode editar e até apagar (não volta a ser criado)."""
        modelo = QuizForm()
        perguntas = []
        for campo, certa in GABARITO_PADRAO.items():
            f = getattr(modelo, campo)
            t = dict(f.choices)
            perguntas.append({'enunciado': re.sub(r'^\d+\.\s*', '', f.label.text), 'opcao_a': t['A'],
                              'opcao_b': t['B'], 'opcao_c': t['C'], 'opcao_d': t['D'],
                              'resposta_correta': certa})
        cls.garantir_padrao(QUIZ_PADRAO_TITULO, 'Célula', perguntas)

    # ── formulário de criação/edição de quiz (admin) ──────────────────────────────────────────
    @staticmethod
    def ler_perguntas(form):
        """Lê as perguntas de um formulário (request.form): p<N>_enunciado, p<N>_a..d, p<N>_correta,
        p<N>_id. Devolve (perguntas, erros)."""
        perguntas, erros = [], []
        total = min(form.get('total', type=int) or 0, MAX_PERGUNTAS_FORM)
        for i in range(1, total + 1):
            if f'p{i}_enunciado' not in form:          # bloco removido na tela
                continue
            d = {'enunciado': form.get(f'p{i}_enunciado', '').strip(),
                 'opcao_a': form.get(f'p{i}_a', '').strip(),
                 'opcao_b': form.get(f'p{i}_b', '').strip(),
                 'opcao_c': form.get(f'p{i}_c', '').strip(),
                 'opcao_d': form.get(f'p{i}_d', '').strip(),
                 'resposta_correta': form.get(f'p{i}_correta', ''),
                 'id': form.get(f'p{i}_id', type=int)}
            vazio = not any(d[k] for k in ('enunciado',) + CAMPOS_TEXTO)
            if vazio and d['id'] is None:
                continue                                # bloco em branco: ignora
            if (not all(d[k] for k in ('enunciado',) + CAMPOS_TEXTO)
                    or d['resposta_correta'] not in LETRAS):
                erros.append(f"Pergunta {len(perguntas) + 1}: preencha o enunciado, as 4 alternativas e marque a correta.")
            elif len(d['enunciado']) > 1000 or any(len(d[k]) > 200 for k in CAMPOS_TEXTO):
                erros.append(f"Pergunta {len(perguntas) + 1}: texto grande demais (alternativas até 200 caracteres).")
            perguntas.append(d)
        return perguntas, erros

    @classmethod
    def validar_dados(cls, titulo, tema, perguntas, ignorar_id=None):
        """Regras do quiz como um todo (título, tema, ao menos uma pergunta). Devolve lista de erros."""
        erros = []
        if not titulo or len(titulo) > 200:
            erros.append("Informe o título do quiz (até 200 caracteres).")
        elif cls.titulo_existe(titulo, ignorar_id=ignorar_id):
            erros.append("Já existe um quiz com este título. Use outro (as estatísticas são separadas por título).")
        if tema not in dict(TEMAS_CONTEUDO):
            erros.append("Escolha o conteúdo (tema) do quiz.")
        if not perguntas:
            erros.append("Adicione ao menos uma pergunta.")
        return erros

    @classmethod
    def perguntas_para_edicao(cls, quiz):
        return [dict(id=p.id, enunciado=p.enunciado, opcao_a=p.opcao_a, opcao_b=p.opcao_b,
                     opcao_c=p.opcao_c, opcao_d=p.opcao_d, resposta_correta=p.resposta_correta)
                for p in cls.perguntas_do_quiz(quiz.id)]

    @staticmethod
    def perguntas_em_branco():
        return [dict(id=None, enunciado='', opcao_a='', opcao_b='', opcao_c='', opcao_d='',
                     resposta_correta='') for _ in range(PERGUNTAS_EM_BRANCO)]
