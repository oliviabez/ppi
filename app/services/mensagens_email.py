"""Textos dos e-mails enviados pelo SiteBio (o envio em si fica no EmailService)."""
from app.constantes import ROTULO_PERFIL, TEMAS_FEEDBACK


def _primeiro_nome(nome):
    return nome.strip().split()[0]


def boas_vindas_cadastro(nome, perfil, url_login):
    """Cadastro concluído na hora (sem confirmação de código)."""
    return (f"Olá, {_primeiro_nome(nome)}!\n\nSeu cadastro no SiteBio "
            f"({ROTULO_PERFIL.get(perfil, perfil)}) foi realizado com sucesso.\n\n"
            f"Entre em: {url_login}\n\nBons estudos!\nEquipe SiteBio — IFRN\n")


def codigo_verificacao(nome, codigo, motivo):
    primeiro = (nome or '').strip().split()[0] if (nome or '').strip() else 'tudo bem'
    return (f"Olá, {primeiro}!\n\nSeu código para {motivo} no SiteBio é:\n\n        {codigo}\n\n"
            "Ele vale por 15 minutos e só pode ser usado por você. Se não foi você que pediu, "
            "ignore este e-mail.\n\nSiteBio — Plataforma educacional de Biologia · IFRN\n")


def contato_estudante(estudante, mensagem):
    """Estudante escrevendo para um administrador."""
    return (f"Mensagem do(a) estudante {estudante.nome} <{estudante.email}>:\n\n"
            f"{mensagem.strip()}\n\n— Enviado pelo SiteBio. Responda este e-mail para falar com o(a) estudante.")


def resposta_duvida(autor, admin, duvida, resposta, url_feedback):
    """Aviso ao estudante de que o administrador respondeu a dúvida dele."""
    return (f"Olá, {autor.nome.split()[0]}!\n\n{admin.nome} respondeu sua dúvida "
            f"({dict(TEMAS_FEEDBACK).get(duvida.tema, duvida.tema)}):\n\n"
            f"Sua dúvida: {duvida.texto}\n\nResposta: {resposta.strip()}\n\n"
            f"Algo mais específico? Responda este e-mail: ele chega direto para {admin.email}.\n"
            f"Você também vê a resposta no site: {url_feedback}\n\n"
            "Equipe SiteBio — IFRN\n")
