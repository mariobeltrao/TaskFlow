class Tarefa:
    def __init__(self, titulo, materia, prazo):
        self.titulo = titulo
        self.materia = materia 
        self.prazo = prazo
        self.concluida = False

    def concluir(self):
        self.concluida = True