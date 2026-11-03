"""Códigos de 6 dígitos enviados por e-mail (confirmação de cadastro e senha esquecida)."""
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from flask import current_app
from app.models.extras import VerificacaoEmail
from app.services.repositorio import Repositorio

VALIDADE_MIN = 15
MAX_TENTATIVAS = 5
INTERVALO_REENVIO_S = 60

_repo = Repositorio(VerificacaoEmail, 'verificacoes', padroes={'tentativas': 0, 'data': datetime.now})


def _hash(tipo, email, codigo):
    base = f"{current_app.secret_key}|{tipo}|{email}|{codigo}".encode()
    return hashlib.sha256(base).hexdigest()


class VerificacaoService:
    def segundos_para_reenviar(self, tipo, email):
        """0 se já pode pedir outro código; senão, quantos segundos faltam."""
        atual = _repo.um(tipo=tipo, email=email)
        if atual is None:
            return 0
        passou = (datetime.now() - atual.data).total_seconds()
        return max(0, int(INTERVALO_REENVIO_S - passou))

    def gerar(self, tipo, email, **extras):
        """Cria (e substitui o anterior) um código. Devolve o código PURO, para ir por e-mail."""
        email = email.strip().lower()
        _repo.excluir_onde(tipo=tipo, email=email)
        codigo = f"{secrets.randbelow(10**6):06d}"
        _repo.adicionar(tipo=tipo, email=email, codigo_hash=_hash(tipo, email, codigo),
                        expira=datetime.now() + timedelta(minutes=VALIDADE_MIN), tentativas=0,
                        nome=extras.get('nome'), senha_hash=extras.get('senha_hash'),
                        perfil=extras.get('perfil'))
        return codigo

    def validar(self, tipo, email, codigo):
        """(registro, None) se o código confere; senão (None, mensagem de erro)."""
        email = (email or '').strip().lower()
        codigo = (codigo or '').strip().replace(' ', '')
        reg = _repo.um(tipo=tipo, email=email)
        if reg is None:
            return None, 'Código inválido ou expirado. Peça um novo código.'
        if datetime.now() > reg.expira or reg.tentativas >= MAX_TENTATIVAS:
            _repo.excluir(reg)
            return None, 'Código expirado ou com tentativas esgotadas. Peça um novo código.'
        if not hmac.compare_digest(reg.codigo_hash, _hash(tipo, email, codigo)):
            reg.tentativas += 1
            _repo.salvar()
            restam = MAX_TENTATIVAS - reg.tentativas
            return None, f'Código incorreto. Tentativas restantes: {restam}.'
        return reg, None

    def consumir(self, reg):
        _repo.excluir(reg)

    def pendente(self, tipo, email):
        return _repo.um(tipo=tipo, email=(email or '').strip().lower())

    def descartar(self, tipo, email):
        _repo.excluir_onde(tipo=tipo, email=(email or '').strip().lower())
