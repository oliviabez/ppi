"""Quizzes criados pelo administrador (um por conteúdo/tema), mesma estrutura do quiz padrão:
perguntas de múltipla escolha com 4 alternativas (A–D) e uma resposta correta."""
from app.models.extras import ConfigSite
from app.models.quiz import Quiz, Pergunta
from app.services.repositorio import Repositorio

_quizzes = Repositorio(Quiz, 'quizzes')
_perguntas = Repositorio(Pergunta, 'perguntas')
_config = Repositorio(ConfigSite, 'config_site')

LETRAS = ('A', 'B', 'C', 'D')


class QuizService:
    def listar(self, tema=None):
        return _quizzes.listar(ordenar='id', **({'tema': tema} if tema else {}))

    def buscar(self, quiz_id):
        return _quizzes.buscar(quiz_id)

    def perguntas_do_quiz(self, quiz_id):
        return _perguntas.listar(ordenar='id', quiz_id=quiz_id)

    def titulo_existe(self, titulo, ignorar_id=None):
        return any(q.titulo.strip().lower() == titulo.strip().lower() and q.id != ignorar_id
                   for q in _quizzes.listar())

    def _dados_pergunta(self, d):
        return dict(enunciado=d['enunciado'].strip(), opcao_a=d['opcao_a'].strip(),
                    opcao_b=d['opcao_b'].strip(), opcao_c=d['opcao_c'].strip(),
                    opcao_d=d['opcao_d'].strip(), resposta_correta=d['resposta_correta'])

    def criar(self, titulo, tema, perguntas):
        quiz = _quizzes.adicionar(titulo=titulo.strip(), tema=tema)
        for p in perguntas:
            _perguntas.adicionar(quiz_id=quiz.id, **self._dados_pergunta(p))
        return quiz

    def atualizar(self, quiz, titulo, tema, perguntas):
        """Perguntas com 'id' são atualizadas; sem 'id' são criadas; as que sumiram são removidas."""
        quiz.titulo, quiz.tema = titulo.strip(), tema
        _quizzes.salvar()
        existentes = {p.id: p for p in self.perguntas_do_quiz(quiz.id)}
        mantidos = set()
        for p in perguntas:
            dados = self._dados_pergunta(p)
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

    def excluir(self, quiz):
        _perguntas.excluir_onde(quiz_id=quiz.id)
        _quizzes.excluir(quiz)

    def corrigir(self, quiz, respostas):
        """respostas = {pergunta.id: 'A'..'D'}. Devolve (acertos, detalhes, faltando)."""
        detalhes, acertos, faltando = [], 0, []
        for n, p in enumerate(self.perguntas_do_quiz(quiz.id), start=1):
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
    def garantir_padrao(self, titulo, tema, perguntas):
        """Copia o quiz padrão para o banco UMA vez. Depois disso o admin pode editar/apagar à vontade
        (a marcação impede que ele volte a ser criado)."""
        if _config.um(chave='quiz_padrao_importado'):
            return
        if not self.titulo_existe(titulo):
            self.criar(titulo, tema, perguntas)
        _config.adicionar(chave='quiz_padrao_importado', valor='1')
