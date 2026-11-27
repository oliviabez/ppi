"""Funções de apoio usadas pelas rotas (permissões, CSRF, datas recentes e página inicial por perfil)."""
from datetime import datetime, timedelta
from functools import wraps
from flask import g, url_for, abort
from app.constantes import PERFIL_ADMIN
from app.forms import AcaoForm


def recente(data, dias=30):
    """True se a data é de até 'dias' dias atrás (selo 'Novo' e avisos)."""
    return bool(data) and datetime.now() - data <= timedelta(days=dias)


def pagina_inicial(usuario):
    """Para onde cada perfil vai depois do login."""
    if usuario.perfil == PERFIL_ADMIN:
        return url_for('admin.admin')
    return url_for('conteudo.modalidades')          # Estudante e Público externo


def perfis_permitidos(*perfis):
    """Restringe a rota a certos perfis. Se o perfil não puder, responde 403."""
    def decorador(funcao):
        @wraps(funcao)
        def envelope(*args, **kwargs):
            if g.usuario is None or g.usuario.perfil not in perfis:
                abort(403)
            return funcao(*args, **kwargs)
        return envelope
    return decorador


def exigir_csrf():
    """Valida o token CSRF dos formulários simples (sair, excluir)."""
    if not AcaoForm().validate_on_submit():
        abort(400)
