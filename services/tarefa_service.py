
class TarefaService:
    def __init__(self):
        self.tarefas = []

    def adicionar(self, tarefa):
        self.tarefas.append(tarefa)

    def listar(self):
        return self.tarefas

    def concluir(self, id):
        tarefa.concluir()

    # def remover(self, id):

    # def editar(self, id):

    # def buscar(self, termo):
        