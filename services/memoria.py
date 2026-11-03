"""
Armazenamento EM MEMÓRIA, usado quando SITEBIO_USAR_BANCO=0 (padrão).

LIMITAÇÃO: tudo some quando o servidor reinicia (o modo debug reinicia a cada alteração de código).
LIMITAÇÃO: as listas abaixo são globais do processo; não é seguro com vários processos/workers.
Serve só para demonstrar o sistema funcionando antes de ligar o banco.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash


class Registro(dict):
    """Dicionário que também aceita acesso por atributo (registro.nome), igual aos models."""

    def __getattr__(self, nome):
        try:
            return self[nome]
        except KeyError:
            raise AttributeError(nome)

    def __setattr__(self, nome, valor):
        self[nome] = valor


USUARIOS = []
CONTEUDOS = []
COMENTARIOS = []
RESULTADOS = []

_contadores = {'usuarios': 0, 'conteudos': 0, 'comentarios': 0, 'resultados': 0}


def proximo_id(tabela):
    _contadores[tabela] = _contadores.get(tabela, 0) + 1
    return _contadores[tabela]


# Tabelas novas (modo memória): criadas sob demanda pelo repositório genérico.
_OUTRAS = {}


def tabela(nome):
    """Lista em memória de uma tabela (as 4 antigas + as novas)."""
    fixas = {'usuarios': USUARIOS, 'conteudos': CONTEUDOS,
             'comentarios': COMENTARIOS, 'resultados': RESULTADOS}
    if nome in fixas:
        return fixas[nome]
    return _OUTRAS.setdefault(nome, [])


def semear_demo():
    """Contas e conteúdo de exemplo para testar cada perfil.

    ATENÇÃO: contas com senha conhecida. Isso só acontece no modo memória (sem banco).
    Antes de publicar/entregar, apague esta função e a chamada em app/__init__.py.
    """
    if USUARIOS:
        return
    demo = [
        ('Administrador Demo', 'admin@sitebio.com', 'admin123', 'Admin'),
        ('Aluno Demo', 'aluno@sitebio.com', 'aluno123', 'Estudante'),
        ('Visitante Demo', 'publico@sitebio.com', 'publico123', 'Publico'),
    ]
    for nome, email, senha, perfil in demo:
        USUARIOS.append(Registro(
            id=proximo_id('usuarios'), nome=nome, email=email,
            senha=generate_password_hash(senha), perfil=perfil, data_cadastro=datetime.now()))
    CONTEUDOS.append(Registro(
        id=proximo_id('conteudos'),
        titulo='Conteúdo de exemplo (publicado pelo administrador)',
        tema='Célula',
        descricao='Exemplo para mostrar como as publicações do painel de admin aparecem para os usuários.',
        texto='Este texto foi cadastrado pelo administrador no painel.\n\n'
              'Entre como admin@sitebio.com para criar, editar ou excluir conteúdos como este.',
        data_criacao=datetime.now()))
