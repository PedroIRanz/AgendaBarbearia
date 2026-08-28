from flask import Flask, render_template, request
from datetime import datetime, timedelta
import json
import os
import re

app = Flask(__name__)


# =========================
# SERVIÇOS
# =========================

SERVICOS = {
    "corte": {
        "nome": "Corte",
        "tempo": 30,
        "valor": 30
    },

    "barba": {
        "nome": "Barba",
        "tempo": 30,
        "valor": 20
    },

    "corte_barba": {
        "nome": "Corte + Barba",
        "tempo": 60,
        "valor": 45
    }
}


# =========================
# ARQUIVO DE AGENDAMENTOS
# =========================

CAMINHO_AGENDAMENTOS = os.path.join(
    os.path.dirname(__file__),
    "agendamentos.json"
)


def carregar_agendamentos():

    if not os.path.exists(CAMINHO_AGENDAMENTOS):
        return []

    with open(
        CAMINHO_AGENDAMENTOS,
        "r",
        encoding="utf-8"
    ) as arquivo:

        conteudo = arquivo.read().strip()

        if conteudo == "":
            return []

        return json.loads(conteudo)


def salvar_agendamentos(agendamentos):

    with open(
        CAMINHO_AGENDAMENTOS,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            agendamentos,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


# =========================
# PÁGINA PRINCIPAL
# =========================

@app.route("/")
def index():
    return render_template("index.html")


# =========================
# FUNÇÕES DE HORÁRIO
# =========================

def horario_para_minutos(horario):

    hora, minuto = horario.split(":")

    return int(hora) * 60 + int(minuto)


def horarios_conflitam(
    inicio1,
    fim1,
    inicio2,
    fim2
):

    return (
        inicio1 < fim2
        and
        fim1 > inicio2
    )


def horario_funcionamento(horario, tempo_servico):

    inicio = horario_para_minutos(horario)

    # Só permite horários de 30 em 30 minutos.
    minuto = inicio % 60

    if minuto not in (0, 30):
        return False

    fim = inicio + tempo_servico

    # Manhã: 09:00 até 12:00
    if inicio >= 9 * 60 and fim <= 12 * 60:
        return True

    # Tarde: 14:00 até 20:00
    if inicio >= 14 * 60 and fim <= 20 * 60:
        return True

    return False


# =========================
# VALIDAÇÕES
# =========================

def nome_valido(nome):

    if not isinstance(nome, str):
        return False

    nome = nome.strip()

    if len(nome.replace(" ", "")) < 3:
        return False

    return bool(
        re.fullmatch(
            r"[A-Za-zÀ-ÿ\s]+",
            nome
        )
    )


def celular_valido(celular):

    if not isinstance(celular, str):
        return False

    somente_numeros = re.sub(
        r"\D",
        "",
        celular
    )

    return len(somente_numeros) == 11


def dia_funcionamento(data):

    data_convertida = datetime.strptime(
        data,
        "%Y-%m-%d"
    )

    dia_semana = data_convertida.weekday()

    # Python:
    # 0 = Segunda
    # 1 = Terça
    # 2 = Quarta
    # 3 = Quinta
    # 4 = Sexta
    # 5 = Sábado
    # 6 = Domingo

    return (
        dia_semana >= 1
        and
        dia_semana <= 5
    )


def data_dentro_do_limite(data):

    data_agendamento = datetime.strptime(
        data,
        "%Y-%m-%d"
    ).date()

    hoje = datetime.now().date()

    data_limite = (
        hoje
        + timedelta(days=14)
    )

    return (
        hoje
        <= data_agendamento
        <= data_limite
    )

def antecedencia_valida(data, horario):

    agora = datetime.now()

    data_hora_agendamento = datetime.strptime(
        f"{data} {horario}",
        "%Y-%m-%d %H:%M"
    )

    antecedencia_minima = agora + timedelta(
        minutes=30
    )

    return data_hora_agendamento >= antecedencia_minima

# =========================
# REALIZAR AGENDAMENTO
# =========================

@app.route("/agendar", methods=["POST"])
def agendar():

    dados = request.get_json(
        silent=True
    )

    # Verifica se realmente recebemos JSON.
    if not isinstance(dados, dict):
        return {
            "erro": "Dados inválidos!"
        }, 400

    # Verifica se os campos necessários existem.
    campos_obrigatorios = [
        "nome",
        "celular",
        "servico",
        "data",
        "horario"
    ]

    for campo in campos_obrigatorios:

        if campo not in dados:
            return {
                "erro": "Dados incompletos!"
            }, 400

    # =========================
    # NOME
    # =========================

    if not nome_valido(
        dados["nome"]
    ):
        return {
            "erro": "Nome inválido!"
        }, 400

    # =========================
    # CELULAR
    # =========================

    if not celular_valido(
        dados["celular"]
    ):
        return {
            "erro": "Celular inválido!"
        }, 400

    # =========================
    # SERVIÇO
    # =========================

    chave_servico = dados["servico"]

    # O JavaScript deve mandar:
    #
    # "corte"
    # "barba"
    # "corte_barba"
    #
    # e não o objeto inteiro.

    if not isinstance(
        chave_servico,
        str
    ):
        return {
            "erro": "Serviço inválido!"
        }, 400

    if chave_servico not in SERVICOS:
        return {
            "erro": "Serviço inválido!"
        }, 400

    # O Flask pega os dados verdadeiros
    # do serviço.
    servico = SERVICOS[
        chave_servico
    ]

    # =========================
    # DATA
    # =========================

    try:

        if not data_dentro_do_limite(
            dados["data"]
        ):
            return {
                "erro": (
                    "A data deve estar entre "
                    "hoje e os próximos 14 dias!"
                )
            }, 400

        if not dia_funcionamento(
            dados["data"]
        ):
            return {
                "erro": (
                    "A barbearia não "
                    "funciona nesse dia!"
                )
            }, 400

    except (ValueError, TypeError):

        return {
            "erro": "Data inválida!"
        }, 400

    # =========================
    # HORÁRIO
    # =========================

    try:

        if not antecedencia_valida(
            dados["data"],
            dados["horario"]
        ):
            return {
                "erro": (
                    "O agendamento deve ser feito "
                    "com pelo menos 30 minutos de antecedência!"
                )
            }, 400

    except (ValueError, TypeError):

        return {
            "erro": "Data ou horário inválido!"
        }, 400

    try:

        if not horario_funcionamento(
            dados["horario"],
            servico["tempo"]
        ):
            return {
                "erro": (
                    "Horário fora do "
                    "funcionamento da barbearia!"
                )
            }, 400

    except (ValueError, TypeError):

        return {
            "erro": "Horário inválido!"
        }, 400

    # =========================
    # MONTA O AGENDAMENTO
    # =========================

    novo_agendamento = {
        "cliente": dados["nome"].strip(),
        "celular": re.sub(
            r"\D",
            "",
            dados["celular"]
        ),
        "servico": servico,
        "data": dados["data"],
        "horario": dados["horario"]
    }

    agendamentos = (
        carregar_agendamentos()
    )

    inicio_novo = horario_para_minutos(
        novo_agendamento["horario"]
    )

    fim_novo = (
        inicio_novo
        + novo_agendamento[
            "servico"
        ]["tempo"]
    )

    # =========================
    # VERIFICA CONFLITOS
    # =========================

    for agendamento in agendamentos:

        # Ignora registros antigos do
        # sistema terminal.
        if "data" not in agendamento:
            continue

        # Só compara agendamentos
        # da mesma data.
        if (
            agendamento["data"]
            !=
            novo_agendamento["data"]
        ):
            continue

        # Ignora algum registro antigo
        # que não tenha a estrutura nova.
        if (
            "horario"
            not in agendamento
            or
            "servico"
            not in agendamento
        ):
            continue

        if not isinstance(
            agendamento["servico"],
            dict
        ):
            continue

        if (
            "tempo"
            not in agendamento["servico"]
        ):
            continue

        inicio_existente = (
            horario_para_minutos(
                agendamento["horario"]
            )
        )

        fim_existente = (
            inicio_existente
            +
            agendamento[
                "servico"
            ]["tempo"]
        )

        if horarios_conflitam(
            inicio_novo,
            fim_novo,
            inicio_existente,
            fim_existente
        ):
            return {
                "erro": (
                    "Esse horário "
                    "já está ocupado!"
                )
            }, 409

    # =========================
    # SALVA
    # =========================

    agendamentos.append(
        novo_agendamento
    )

    salvar_agendamentos(
        agendamentos
    )

    print(
        "Agendamento salvo:"
    )

    print(
        novo_agendamento
    )

    return {
        "mensagem": (
            "Agendamento salvo "
            "com sucesso!"
        )
    }


# =========================
# BUSCAR AGENDAMENTOS DO DIA
# =========================

@app.route(
    "/agendamentos/<data>",
    methods=["GET"]
)
def buscar_agendamentos(data):

    agendamentos = (
        carregar_agendamentos()
    )

    agendamentos_do_dia = []

    for agendamento in agendamentos:

        # Ignora registros antigos
        # sem uma data específica.
        if "data" not in agendamento:
            continue

        if agendamento["data"] == data:

            agendamentos_do_dia.append(
                agendamento
            )

    return agendamentos_do_dia


# =========================
# INICIAR FLASK
# =========================

if __name__ == "__main__":
    app.run(debug=True)