from models.tarefa import Tarefa
from services.tarefa_service import TarefaService

service = TarefaService()

tarefa1 = Tarefa(
        "Estudar Python",
        "Programação",
        "12/12/2026"
)



def mostrar_menu():
    print("======================")
    print("       TASKFLOW       ")
    print("======================")
    print("1. Adicionar Tarefa")
    print("2. Listar tarefas")
    print("3. Concluir tarefa")
    print("4. Sair")


while True:
    mostrar_menu()

    opcao = input("Escolha: ")

    if opcao == "1":
        titulo = input("Título: ")
        materia = input("Matéria: ")
        prazo = input("Prazo: ")

        tarefa = Tarefa(titulo, materia, prazo)
        service.adicionar(tarefa)
        pass

    elif opcao == "2":
        tarefas = service.listar()


        for tarefa in tarefas:
            print(tarefa.titulo)
            print(tarefa.materia)
            print(tarefa.prazo)
            print()
            break

    elif opcao == "3":
       service.listar()

    elif opcao == "4":
        print("Saindo...")
        break

    else:
        print("Opção inválida!")