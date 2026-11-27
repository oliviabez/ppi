"""Área de estudo (estudante/público): modalidades e páginas de conteúdo."""
from flask import Blueprint, render_template, g, abort
from app.constantes import PERFIL_ESTUDANTE
from app.services import (ConteudoService, ResultadoService, ImagemService, RespostaQuizService,
                          FeedbackService, imagem_texto)
from app.utils import recente

bp = Blueprint('conteudo', __name__)


@bp.route('/modalidades')
def modalidades():
    resultados, duvidas = [], []
    if g.usuario.perfil == PERFIL_ESTUDANTE:
        resultados = ResultadoService.listar_do_usuario(g.usuario.id, limite=5)
        duvidas = [d for d in RespostaQuizService.duvidas_por_tema(g.usuario.id) if d['erros']][:2]
    return render_template('shared/modalidades.html',
                           conteudos=[c for c in ConteudoService.listar_todos()
                                      if recente(c.data_criacao)],       # aviso de 30 dias
                           resultados=resultados, duvidas=duvidas,
                           depoimentos=FeedbackService.listar_publicados())


@bp.route('/conteudo/<int:conteudo_id>')
def conteudo(conteudo_id):
    item = ConteudoService.buscar(conteudo_id)
    if item is None:
        abort(404)
    imagens = ImagemService.listar_conteudo(conteudo_id)
    return render_template('conteudo/conteudo.html', conteudo=item, imagens=imagens,
                           imagens_livres=imagem_texto.livres(imagens, [item.texto]))   # as não citadas no texto


@bp.route('/celula')
def celula():
    return render_template('conteudo/celula.html')


@bp.route('/citologia')
def citologia():
    return render_template('conteudo/citologia.html')


@bp.route('/dna')
def dna():
    return render_template('conteudo/dna.html')


@bp.route('/continuidade')
def cont():
    return render_template('conteudo/cont.html')


@bp.route('/educacao-sexual')
def ed_sex():
    return render_template('conteudo/ed_sex.html')


@bp.route('/manutencao')
def manutencao():
    return render_template('conteudo/manutencao.html')
