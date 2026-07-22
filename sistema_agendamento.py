"""
Sistema de Agendamentos - Barbearia
"""

import json
import os


# ==========================
# Banco
# ==========================

diasdis = [
    "Terça-feira",
    "Quarta-feira",
    "Quinta-feira",
    "Sexta-feira",
    "Sábado"
]


hrsdis = [
    "9H", "10H", "11H", "12H",
    "14H", "15H", "16H",
    "17H", "18H", "19H"
]


precos = {
    "Corte": {"tempo": 30, "valor": 30.0},
    "Barba": {"tempo": 30, "valor": 20.0},
    "Cabelo + Barba": {"tempo": 60, "valor": 45.0}
}



# ==========================
# Arquivo
# ==========================

def carregar_agendamentos():

    if os.path.exists("agendamentos.json"):

        try:
            with open(
                "agendamentos.json",
                "r",
                encoding="utf-8"
            ) as arquivo:

                return json.load(arquivo)

        except json.JSONDecodeError:
            print("Arquivo de agendamentos vazio. Criando novo banco...")
            return []

    return []


def salvar_agendamentos():

    with open(
        "agendamentos.json",
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            agendamentos,
            arquivo,
            indent=4,
            ensure_ascii=False
        )



agendamentos = carregar_agendamentos()



# ==========================
# Funções
# ==========================

def horario_disponivel(dia, horario):

    for agendamento in agendamentos:

        if (
            agendamento["dia"] == dia
            and agendamento["horario"] == horario
        ):
            return False


    return True



def escolher_servico():

    print("\n===== SERVIÇOS =====")


    for i, (nome, dados) in enumerate(precos.items(), start=1):

        print(
            f"{i} - {nome} "
            f"{dados['tempo']} min "
            f"R$ {dados['valor']:.2f}"
        )


    while True:

        opcao = input("\nEscolha: ")


        if opcao.isdigit() and 1 <= int(opcao) <= len(precos):

            servicos = list(precos.items())

            return servicos[int(opcao)-1]


        print("Opção inválida!")



def escolher_dia():

    print("\n===== DIAS DISPONÍVEIS =====")


    for i, dia in enumerate(diasdis, start=1):

        print(f"{i} - {dia}")


    while True:

        opcao = input("\nEscolha o dia: ")


        if opcao.isdigit() and 1 <= int(opcao) <= len(diasdis):

            return diasdis[int(opcao)-1]


        print("Escolha um número válido!")



def escolher_horario(dia):

    print("\n===== HORÁRIOS =====")


    for i, hora in enumerate(hrsdis, start=1):

        print(f"{i} - {hora}")


    while True:

        opcao = input("\nEscolha o horário: ")


        if opcao.isdigit() and 1 <= int(opcao) <= len(hrsdis):

            horario = hrsdis[int(opcao)-1]


            if horario_disponivel(dia, horario):

                return horario


            else:

                print("Esse horário já está ocupado!")


        else:

            print("Opção inválida!")



def validar_nome():

    while True:

        nome = input("\nQual o seu nome? ").strip()


        nome_limpo = nome.replace(" ", "")


        if nome_limpo.isalpha() and len(nome_limpo) >= 3:

            return nome


        print(
            "Nome inválido! "
            "Use somente letras e mínimo 3 caracteres."
        )



def novo_agendamento():

    servico, dados = escolher_servico()


    dia = escolher_dia()


    horario = escolher_horario(dia)


    nome = validar_nome()



    print("\n===== RESUMO =====")

    print(f"Cliente: {nome}")
    print(f"Serviço: {servico}")
    print(f"Dia: {dia}")
    print(f"Horário: {horario}")
    print(f"Valor: R$ {dados['valor']:.2f}")

    print("==================")



    while True:

        confirmar = input(
            "\nConfirmar? (1-Sim / 2-Não): "
        )


        if confirmar == "1":

            agendamentos.append({

                "cliente": nome,
                "servico": servico,
                "dia": dia,
                "horario": horario

            })


            salvar_agendamentos()


            print(
                "\nAgendamento realizado com sucesso!"
            )

            break



        elif confirmar == "2":

            print(
                "\nAgendamento cancelado."
            )

            break



        else:

            print("Opção inválida!")



def ver_agendamentos():

    print("\n===== AGENDAMENTOS =====")


    if not agendamentos:

        print("Nenhum agendamento.")


    else:

        for i, ag in enumerate(agendamentos, start=1):

            print(f"\nAgendamento {i}")

            print(f"Cliente: {ag['cliente']}")
            print(f"Serviço: {ag['servico']}")
            print(f"Dia: {ag['dia']}")
            print(f"Horário: {ag['horario']}")


    print("========================")



def cancelar_agendamento():

    if not agendamentos:

        print("\nNenhum agendamento para cancelar.")

        return



    ver_agendamentos()



    while True:

        escolha = input(
            "\nNúmero do agendamento: "
        )


        if escolha.isdigit() and 1 <= int(escolha) <= len(agendamentos):

            removido = agendamentos.pop(
                int(escolha)-1
            )


            salvar_agendamentos()


            print(
                f"\nCancelado: {removido['cliente']}"
            )

            break


        else:

            print("Número inválido!")



# ==========================
# Menu
# ==========================

while True:


    print("\n===== BARBEARIA PEDRO IVES =====")

    print("1 - Novo agendamento")
    print("2 - Ver agendamentos")
    print("3 - Cancelar agendamento")
    print("4 - Sair")


    escolha = input("\nEscolha: ")



    if escolha == "1":

        novo_agendamento()



    elif escolha == "2":

        ver_agendamentos()



    elif escolha == "3":

        cancelar_agendamento()



    elif escolha == "4":

        print("Sistema encerrado.")

        break



    else:

        print("Opção inválida!")