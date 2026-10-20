class UsuarioService:
    def __init__(self):
        self.usuarios = []

    def cadastrar(self, usuario):
        self.usuarios.append(usuario)
        return usuario

    def listar_todos(self):
        return self.usuarios
