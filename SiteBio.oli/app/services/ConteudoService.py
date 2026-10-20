class ConteudoService:
    def __init__(self):
        self.conteudos = []

    def adicionar(self, conteudo):
        self.conteudos.append(conteudo)
        return conteudo

    def listar_todos(self):
        return self.conteudos
