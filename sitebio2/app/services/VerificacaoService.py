"""Códigos de 6 dígitos enviados por e-mail: confirmar o cadastro e redefinir a senha esquecida."""
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from flask import current_app
from app.models.verificacao_email import VerificacaoEmail
from app.services.DBRepository import DBRepository

VALIDADE_MIN = 15
MAX_TENTATIVAS = 5
INTERVALO_REENVIO_S = 60

_repo = DBRepository(VerificacaoEmail)


def _hash(tipo, email, codigo):
    base = f"{current_app.secret_key}|{tipo}|{email}|{codigo}".encode()
    return hashlib.sha256(base).hexdigest()


class VerificacaoService:
    @staticmethod
    def segundos_para_reenviar(tipo, email):
        """0 se já pode pedir outro código; senão, quantos segundos faltam."""
        atual = _repo.um(tipo=tipo, email=email)
        if atual is None:
            return 0
        passou = (datetime.now() - atual.data).total_seconds()
        return max(0, int(INTERVALO_REENVIO_S - passou))

    @staticmethod
    def gerar(tipo, email, **dados):
        """Cria (e substitui o anterior) um código. Devolve o código PURO, para ir por e-mail.
        'dados' guarda campos extras do registro (usado no cadastro: nome, senha_hash, perfil...)."""
        email = email.strip().lower()
        _repo.excluir_onde(tipo=tipo, email=email)
        codigo = f"{secrets.randbelow(10**6):06d}"
        _repo.adicionar(tipo=tipo, email=email, codigo_hash=_hash(tipo, email, codigo),
                        expira=datetime.now() + timedelta(minutes=VALIDADE_MIN), tentativas=0, **dados)
        return codigo

    @staticmethod
    def validar(tipo, email, codigo):
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

    @staticmethod
    def cancelar(tipo, email):
        """Apaga o código pendente (ex.: o e-mail não pôde ser enviado)."""
        _repo.excluir_onde(tipo=tipo, email=(email or '').strip().lower())

    @staticmethod
    def consumir(reg):
        _repo.excluir(reg)
