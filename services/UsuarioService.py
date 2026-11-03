from datetime import datetime
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.usuario import Usuario
from app.services import memoria
from app.services.memoria import Registro


def _usar_banco():
    return current_app.config['USAR_BANCO']


class UsuarioService:
    """Cadastro, login e edição de usuários. Funciona em memória ou no banco (ver app/__init__.py)."""

    # ATENÇÃO: e-mails são guardados em minúsculas para o login não depender de maiúsculas.

    def cadastrar(self, dados):
        email = dados['email'].strip().lower()
        # NOVO: o cadastro confirmado por e-mail já chega com o hash pronto ('senha_hash').
        senha_hash = dados.get('senha_hash') or generate_password_hash(dados['senha'])
        if _usar_banco():
            from app import db
            novo = Usuario(nome=dados['nome'].strip(), email=email,
                           perfil=dados['perfil'], senha=senha_hash)
            db.session.add(novo)
            db.session.commit()
            return novo
        novo = Registro(id=memoria.proximo_id('usuarios'), nome=dados['nome'].strip(), email=email,
                        perfil=dados['perfil'], senha=senha_hash, data_cadastro=datetime.now())
        memoria.USUARIOS.append(novo)
        return novo

    def buscar_por_id(self, usuario_id):
        if _usar_banco():
            from app import db
            return db.session.get(Usuario, usuario_id)
        return next((u for u in memoria.USUARIOS if u.id == usuario_id), None)

    def buscar_por_email(self, email):
        email = (email or '').strip().lower()
        if _usar_banco():
            return Usuario.query.filter_by(email=email).first()
        return next((u for u in memoria.USUARIOS if u.email == email), None)

    def autenticar(self, email, senha):
        """Devolve o usuário se e-mail e senha conferem; senão, None."""
        # LIMITAÇÃO: não há bloqueio após várias tentativas erradas (força bruta).
        # TODO: limitar tentativas por IP/e-mail (ex.: Flask-Limiter) antes de publicar.
        usuario = self.buscar_por_email(email)
        if usuario and check_password_hash(usuario.senha, senha):
            return usuario
        return None

    def atualizar(self, usuario_id, dados):
        """Atualiza nome/e-mail e, se vier 'senha', troca a senha. O PERFIL nunca é alterado aqui
        (senão um estudante poderia se promover a admin editando o cadastro)."""
        usuario = self.buscar_por_id(usuario_id)
        if usuario is None:
            return None
        usuario.nome = dados['nome'].strip()
        usuario.email = dados['email'].strip().lower()
        if dados.get('senha'):
            usuario.senha = generate_password_hash(dados['senha'])
        if _usar_banco():
            from app import db
            db.session.commit()
        return usuario

    def excluir(self, usuario_id):
        usuario = self.buscar_por_id(usuario_id)
        if usuario is None:
            return False
        if _usar_banco():
            from app import db
            db.session.delete(usuario)      # cascade apaga comentários e resultados
            db.session.commit()
        else:
            memoria.USUARIOS.remove(usuario)
            memoria.COMENTARIOS[:] = [c for c in memoria.COMENTARIOS if c.usuario_id != usuario_id]
            memoria.RESULTADOS[:] = [r for r in memoria.RESULTADOS if r.usuario_id != usuario_id]
        return True

    def listar_todos(self):
        if _usar_banco():
            return Usuario.query.order_by(Usuario.id).all()
        return list(memoria.USUARIOS)

    def contar_por_perfil(self):
        contagem = {'Estudante': 0, 'Publico': 0, 'Admin': 0}
        for u in self.listar_todos():
            contagem[u.perfil] = contagem.get(u.perfil, 0) + 1
        return contagem
