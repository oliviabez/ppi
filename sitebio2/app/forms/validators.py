"""Validadores compartilhados pelos formulários."""
from wtforms.validators import Regexp

# Validador de e-mail próprio (formato básico: algo@dominio.ext).
# Motivo: o validador Email() do WTForms exige o pacote "email-validator"; se ele não estiver
# instalado, o login/cadastro quebra com "Internal Server Error". Assim não há dependência extra.
Email = lambda: Regexp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', message='Informe um e-mail válido.')

# Código de 6 números enviado por e-mail (aceita um espaço no meio: "123 456").
Codigo = lambda: Regexp(r'^\s*\d{3}\s?\d{3}\s*$', message='O código tem 6 números.')
