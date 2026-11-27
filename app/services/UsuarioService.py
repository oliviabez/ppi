import hmac
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.constantes import PERFIL_ESTUDANTE, PERFIL_PUBLICO, PERFIL_ADMIN
from app.models.usuario import Usuario


class UsuarioService:
    """Cadastro, autenticação, edição e exclusão de usuários no MySQL."""

    @staticmethod
    def gerar_hash(texto):
        return generate_password_hash(texto)

    @staticmethod
    def cadastrar_de_verificacao(reg):
        """Cria a conta a partir do registro de verificação (e-mail já confirmado)."""
        novo = Usuario(nome=reg.nome.strip(), email=reg.email, perfil=reg.perfil, senha=reg.senha_hash)
        db.session.add(novo)
        db.session.commit()
        return novo

    @staticmethod
    def codigo_admin_correto(codigo):
        """Confere o código de administrador digitado com o do .env (SITEBIO_ADMIN_CODIGO).
        Se o .env não define o código, ninguém passa (o acesso de admin fica desativado)."""
        esperado = current_app.config.get('ADMIN_CODIGO', '')
        return bool(esperado) and hmac.compare_digest((codigo or '').strip().encode(), esperado.encode())

    @classmethod
    def validar_cadastro(cls, email, perfil, codigo_admin):
        """Regras do cadastro que o formulário não cobre. Devolve {campo: mensagem de erro}."""
        erros = {}
        if cls.buscar_por_email(email):
            erros['email'] = "Já existe uma conta com este e-mail."
        if perfil == PERFIL_ADMIN:
            if not current_app.config.get('ADMIN_CODIGO'):
                erros['codigo_admin'] = ("O cadastro de administradores está desativado "
                                         "(SITEBIO_ADMIN_CODIGO não foi definido no .env).")
            elif not cls.codigo_admin_correto(codigo_admin):
                erros['codigo_admin'] = "Código de administrador incorreto."
        return erros

    @staticmethod
    def buscar_por_id(usuario_id):
        return db.session.get(Usuario, usuario_id)

    @staticmethod
    def buscar_por_email(email):
        return Usuario.query.filter_by(email=(email or "").strip().lower()).first()

    @classmethod
    def autenticar(cls, email, senha):
        usuario = cls.buscar_por_email(email)
        return usuario if usuario and check_password_hash(usuario.senha, senha) else None

    @classmethod
    def codigo_admin_confere(cls, usuario, codigo):
        """Não-admin: sempre True. Admin: o código digitado precisa ser o do .env."""
        return usuario.perfil != PERFIL_ADMIN or cls.codigo_admin_correto(codigo)

    @classmethod
    def atualizar(cls, usuario_id, dados):
        usuario = cls.buscar_por_id(usuario_id)
        if usuario is None:
            return None
        usuario.nome = dados["nome"].strip()
        usuario.email = dados["email"].strip().lower()
        if dados.get("senha"):
            usuario.senha = generate_password_hash(dados["senha"])
        db.session.commit()
        return usuario

    @classmethod
    def excluir(cls, usuario_id):
        usuario = cls.buscar_por_id(usuario_id)
        if usuario is None:
            return False
        db.session.delete(usuario)
        db.session.commit()
        return True

    @staticmethod
    def listar_todos():
        return Usuario.query.order_by(Usuario.id).all()

    @classmethod
    def contar_por_perfil(cls):
        contagem = {PERFIL_ESTUDANTE: 0, PERFIL_PUBLICO: 0, PERFIL_ADMIN: 0}
        for usuario in cls.listar_todos():
            contagem[usuario.perfil] = contagem.get(usuario.perfil, 0) + 1
        return contagem
