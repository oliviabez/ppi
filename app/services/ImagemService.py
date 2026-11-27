"""Imagens de conteúdos publicados e de páginas fixas (upload do administrador)."""
import os
import uuid
from flask import current_app
from app.constantes import EXTENSOES_IMAGEM
from app.models.imagem_conteudo import ImagemConteudo
from app.services.DBRepository import DBRepository

TAMANHO_MAX = 5 * 1024 * 1024      # 5 MB por imagem

_repo = DBRepository(ImagemConteudo)


def _tipo_real(cabecalho):
    """Descobre o tipo pelos primeiros bytes (não confia só na extensão do nome)."""
    if cabecalho.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'png'
    if cabecalho.startswith(b'\xff\xd8\xff'):
        return 'jpg'
    if cabecalho[:6] in (b'GIF87a', b'GIF89a'):
        return 'gif'
    if cabecalho[:4] == b'RIFF' and cabecalho[8:12] == b'WEBP':
        return 'webp'
    return None


class ImagemService:
    @staticmethod
    def listar_conteudo(conteudo_id):
        return _repo.listar(conteudo_id=conteudo_id)

    @staticmethod
    def listar_pagina(pagina):
        return _repo.listar(pagina=pagina)

    @staticmethod
    def buscar(imagem_id):
        return _repo.buscar(imagem_id)

    @staticmethod
    def salvar_uploads(arquivos, legenda='', conteudo_id=None, pagina=None):
        """Valida e grava as imagens. Devolve (quantas_salvas, [mensagens de erro])."""
        pasta = current_app.config['PASTA_UPLOADS']
        os.makedirs(pasta, exist_ok=True)
        salvas, erros = 0, []
        for arq in arquivos:
            if not arq or not arq.filename:
                continue
            nome = arq.filename
            ext = nome.rsplit('.', 1)[-1].lower() if '.' in nome else ''
            dados = arq.read(TAMANHO_MAX + 1)
            if ext not in EXTENSOES_IMAGEM:
                erros.append(f"'{nome}': formato não aceito (use PNG, JPG, GIF ou WEBP).")
            elif len(dados) > TAMANHO_MAX:
                erros.append(f"'{nome}': maior que 5 MB.")
            elif _tipo_real(dados[:16]) is None:
                erros.append(f"'{nome}': o arquivo não é uma imagem válida.")
            else:
                final = f"{uuid.uuid4().hex}.{_tipo_real(dados[:16])}"
                with open(os.path.join(pasta, final), 'wb') as f:
                    f.write(dados)
                _repo.adicionar(conteudo_id=conteudo_id, pagina=pagina, arquivo=final,
                                legenda=(legenda or '').strip()[:200] or None)
                salvas += 1
        return salvas, erros

    @staticmethod
    def excluir(imagem):
        caminho = os.path.join(current_app.config['PASTA_UPLOADS'], imagem.arquivo)
        _repo.excluir(imagem)
        try:
            os.remove(caminho)
        except OSError:
            pass

    @classmethod
    def excluir_do_conteudo(cls, conteudo_id):
        """Apaga os arquivos e os registros das imagens de um conteúdo que foi excluído."""
        for img in cls.listar_conteudo(conteudo_id):
            cls.excluir(img)
