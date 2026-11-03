"""Envio de e-mails (SMTP).

Configure por variáveis de ambiente (ver README):
    SITEBIO_SMTP_HOST, SITEBIO_SMTP_PORT, SITEBIO_SMTP_USUARIO, SITEBIO_SMTP_SENHA, SITEBIO_EMAIL_REMETENTE

LIMITAÇÃO: se SITEBIO_SMTP_HOST estiver vazio, o e-mail NÃO sai de verdade: o conteúdo é impresso
no terminal (modo desenvolvimento). Em produção, configure o SMTP.
"""
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr
from flask import current_app


def email_configurado():
    return bool(current_app.config.get('SMTP_HOST'))


class EmailService:
    def enviar(self, destino, assunto, texto, reply_to=None):
        """Devolve True se foi enviado (ou impresso no modo dev) e False se deu erro."""
        cfg = current_app.config
        if not cfg.get('SMTP_HOST'):
            print('\n' + '=' * 70 + '\n[SiteBio · MODO DEV — SMTP não configurado, e-mail não enviado]'
                  f'\nPara: {destino}\nAssunto: {assunto}\n' + (f'Responder para: {reply_to}\n' if reply_to else '')
                  + '-' * 70 + f'\n{texto}\n' + '=' * 70 + '\n', flush=True)
            return True

        remetente = cfg.get('EMAIL_REMETENTE') or cfg.get('SMTP_USUARIO')
        msg = EmailMessage()
        msg['Subject'] = assunto
        msg['From'] = formataddr(('SiteBio IFRN', remetente))
        msg['To'] = destino
        if reply_to:
            msg['Reply-To'] = reply_to
        msg.set_content(texto)
        try:
            porta = cfg['SMTP_PORT']
            if porta == 465:
                with smtplib.SMTP_SSL(cfg['SMTP_HOST'], porta, timeout=15,
                                      context=ssl.create_default_context()) as s:
                    self._login_e_envio(s, cfg, msg)
            else:
                with smtplib.SMTP(cfg['SMTP_HOST'], porta, timeout=15) as s:
                    s.starttls(context=ssl.create_default_context())
                    self._login_e_envio(s, cfg, msg)
            return True
        except (smtplib.SMTPException, OSError) as erro:
            current_app.logger.error('Falha ao enviar e-mail para %s: %s', destino, erro)
            print(f'\n[SiteBio · ERRO AO ENVIAR E-MAIL] para {destino}: {type(erro).__name__}: {erro}\n'
                  f'Servidor: {cfg["SMTP_HOST"]}:{cfg["SMTP_PORT"]} · usuário: {cfg["SMTP_USUARIO"]}\n', flush=True)
            return False

    @staticmethod
    def _login_e_envio(servidor, cfg, msg):
        if cfg.get('SMTP_USUARIO'):
            servidor.login(cfg['SMTP_USUARIO'], cfg['SMTP_SENHA'])
        servidor.send_message(msg)
