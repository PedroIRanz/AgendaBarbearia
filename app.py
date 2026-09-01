from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for
)
from datetime import datetime, timedelta
import json
import os
import re
import secrets
from functools import wraps

from banco import (
    criar_tabelas,
    autenticar_usuario,
    buscar_usuario_por_id,
    listar_usuarios,
    criar_usuario,
    editar_usuario,
    alterar_senha,
    definir_usuario_ativo,
    listar_profissionais_ativos,
    buscar_profissional_ativo,
    definir_disponibilidade_agendamentos,
    buscar_agendamentos_sqlite,
    listar_agendamentos_colaborador,
    listar_agendamentos_futuros,
    buscar_agendamento_por_id,
    criar_agendamento_sqlite,
    cancelar_agendamento_sqlite,
    migrar_agendamentos_legados
)

app = Flask(__name__)


# =========================
# SESSÃO / LOGIN
# =========================

# Em produção, defina SECRET_KEY
# como variável de ambiente.
#
# No desenvolvimento local,
# uma chave temporária é criada
# quando o Flask inicia.
app.config["SECRET_KEY"] = (
    os.environ.get("SECRET_KEY")
    or secrets.token_hex(32)
)

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Cria as tabelas do banco caso
# ainda não existam.
criar_tabelas()


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
# FUNCIONAMENTO NORMAL
# =========================

PERIODOS_NORMAIS = [
    {
        "inicio": "09:00",
        "fim": "12:00"
    },

    {
        "inicio": "14:00",
        "fim": "20:00"
    }
]


# =========================
# ARQUIVOS
# =========================

CAMINHO_AGENDAMENTOS = os.path.join(
    os.path.dirname(__file__),
    "agendamentos.json"
)

CAMINHO_DIAS_ESPECIAIS = os.path.join(
    os.path.dirname(__file__),
    "dias_especiais.json"
)


# =========================
# AGENDAMENTOS
# =========================

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
# DIAS ESPECIAIS
# =========================

def carregar_dias_especiais():

    if not os.path.exists(
        CAMINHO_DIAS_ESPECIAIS
    ):
        return []

    with open(
        CAMINHO_DIAS_ESPECIAIS,
        "r",
        encoding="utf-8"
    ) as arquivo:

        conteudo = arquivo.read().strip()

        if conteudo == "":
            return []

        return json.loads(conteudo)


def salvar_dias_especiais(
    dias_especiais
):

    with open(
        CAMINHO_DIAS_ESPECIAIS,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            dias_especiais,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


def buscar_dia_especial(data):

    dias_especiais = (
        carregar_dias_especiais()
    )

    for dia in dias_especiais:

        if dia["data"] == data:
            return dia

    return None


# =========================
# MIGRAÇÃO DO JSON ANTIGO
# =========================

def migrar_json_antigo_para_sqlite():

    agendamentos_antigos = (
        carregar_agendamentos()
    )

    if not agendamentos_antigos:
        return

    usuarios = listar_usuarios(
        somente_ativos=True
    )

    dono = None

    for usuario in usuarios:

        if usuario["cargo"] == "dono":

            dono = usuario
            break

    if dono is None:
        return

    registros = []

    for agendamento in agendamentos_antigos:

        if not isinstance(
            agendamento,
            dict
        ):
            continue

        try:

            cliente = str(
                agendamento["cliente"]
            ).strip()

            celular = re.sub(
                r"\D",
                "",
                str(
                    agendamento["celular"]
                )
            )

            data = agendamento["data"]
            horario = agendamento["horario"]
            servico_antigo = agendamento["servico"]

            datetime.strptime(
                data,
                "%Y-%m-%d"
            )

            datetime.strptime(
                horario,
                "%H:%M"
            )

            if not isinstance(
                servico_antigo,
                dict
            ):
                continue

            chave_encontrada = None

            for chave, servico in SERVICOS.items():

                if (
                    servico_antigo.get("nome")
                    ==
                    servico["nome"]
                ):

                    chave_encontrada = chave
                    break

            if chave_encontrada is None:
                continue

            servico = SERVICOS[
                chave_encontrada
            ]

            registros.append({
                "cliente": cliente,
                "celular": celular,
                "servico_chave": chave_encontrada,
                "servico_nome": servico["nome"],
                "servico_tempo": servico["tempo"],
                "servico_valor": servico["valor"],
                "data": data,
                "horario": horario
            })

        except (
            KeyError,
            ValueError,
            TypeError
        ):

            continue

    quantidade = migrar_agendamentos_legados(
        registros,
        colaborador_id=dono["id"]
    )

    if quantidade > 0:

        print(
            f"{quantidade} agendamento(s) antigo(s) "
            "migrado(s) para o SQLite."
        )


migrar_json_antigo_para_sqlite()


# =========================
# PÁGINA PRINCIPAL
# =========================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# =========================
# FUNÇÕES DE HORÁRIO
# =========================

def horario_para_minutos(horario):

    hora, minuto = horario.split(":")

    return (
        int(hora) * 60
        + int(minuto)
    )


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


# =========================
# VALIDA PERÍODOS ESPECIAIS
# =========================

def periodos_validos(periodos):

    if not isinstance(
        periodos,
        list
    ):
        return False

    # Se o dia estiver aberto,
    # precisa ter pelo menos
    # um período.
    if len(periodos) == 0:
        return False

    periodos_convertidos = []

    for periodo in periodos:

        if not isinstance(
            periodo,
            dict
        ):
            return False

        if (
            "inicio" not in periodo
            or
            "fim" not in periodo
        ):
            return False

        inicio_texto = (
            periodo["inicio"]
        )

        fim_texto = (
            periodo["fim"]
        )

        # Os horários precisam estar
        # no formato HH:MM e trabalhar
        # de 30 em 30 minutos.
        padrao_horario = (
            r"(?:[01]\d|2[0-3]):"
            r"(?:00|30)"
        )

        if not isinstance(
            inicio_texto,
            str
        ):
            return False

        if not isinstance(
            fim_texto,
            str
        ):
            return False

        if not re.fullmatch(
            padrao_horario,
            inicio_texto
        ):
            return False

        if not re.fullmatch(
            padrao_horario,
            fim_texto
        ):
            return False

        try:

            inicio = (
                horario_para_minutos(
                    inicio_texto
                )
            )

            fim = (
                horario_para_minutos(
                    fim_texto
                )
            )

        except (
            ValueError,
            TypeError,
            AttributeError
        ):
            return False

        # Exemplo inválido:
        #
        # 15:00 até 10:00
        if fim <= inicio:
            return False

        periodos_convertidos.append({
            "inicio": inicio,
            "fim": fim
        })


    # =========================
    # VERIFICA SOBREPOSIÇÃO
    # =========================

    for i in range(
        len(periodos_convertidos)
    ):

        inicio1 = (
            periodos_convertidos[i][
                "inicio"
            ]
        )

        fim1 = (
            periodos_convertidos[i][
                "fim"
            ]
        )

        for j in range(
            i + 1,
            len(periodos_convertidos)
        ):

            inicio2 = (
                periodos_convertidos[j][
                    "inicio"
                ]
            )

            fim2 = (
                periodos_convertidos[j][
                    "fim"
                ]
            )

            if horarios_conflitam(
                inicio1,
                fim1,
                inicio2,
                fim2
            ):
                return False

    return True


def horario_cabe_em_periodos(
    horario,
    tempo_servico,
    periodos
):

    inicio = horario_para_minutos(
        horario
    )

    fim = (
        inicio
        + tempo_servico
    )

    for periodo in periodos:

        inicio_periodo = (
            horario_para_minutos(
                periodo["inicio"]
            )
        )

        fim_periodo = (
            horario_para_minutos(
                periodo["fim"]
            )
        )

        if (
            inicio >= inicio_periodo
            and
            fim <= fim_periodo
        ):
            return True

    return False


def dia_funcionamento_normal(data):

    data_convertida = datetime.strptime(
        data,
        "%Y-%m-%d"
    )

    dia_semana = (
        data_convertida.weekday()
    )

    return (
        dia_semana >= 1
        and
        dia_semana <= 5
    )


def horario_funcionamento_normal(
    data,
    horario,
    tempo_servico
):

    if not dia_funcionamento_normal(
        data
    ):
        return False

    inicio = horario_para_minutos(
        horario
    )

    minuto = inicio % 60

    if minuto not in (0, 30):
        return False

    return horario_cabe_em_periodos(
        horario,
        tempo_servico,
        PERIODOS_NORMAIS
    )


def horario_funcionamento(
    data,
    horario,
    tempo_servico
):

    inicio = horario_para_minutos(
        horario
    )

    minuto = inicio % 60

    if minuto not in (0, 30):
        return False

    fim = inicio + tempo_servico

    dia_especial = buscar_dia_especial(
        data
    )

    # Se existir um dia especial,
    # usa os horários configurados nele.
    if dia_especial is not None:

        if not dia_especial["aberto"]:
            return False

        for periodo in (
            dia_especial["periodos"]
        ):

            inicio_periodo = (
                horario_para_minutos(
                    periodo["inicio"]
                )
            )

            fim_periodo = (
                horario_para_minutos(
                    periodo["fim"]
                )
            )

            if (
                inicio >= inicio_periodo
                and
                fim <= fim_periodo
            ):
                return True

        return False

    # Funcionamento normal da manhã
    if (
        inicio >= 9 * 60
        and
        fim <= 12 * 60
    ):
        return True

    # Funcionamento normal da tarde
    if (
        inicio >= 14 * 60
        and
        fim <= 20 * 60
    ):
        return True

    return False


# =========================
# VALIDAÇÕES
# =========================

def nome_valido(nome):

    if not isinstance(nome, str):
        return False

    nome = nome.strip()

    if len(
        nome.replace(" ", "")
    ) < 3:
        return False

    return bool(
        re.fullmatch(
            r"[A-Za-zÀ-ÿ\s]+",
            nome
        )
    )


def celular_valido(celular):

    if not isinstance(
        celular,
        str
    ):
        return False

    somente_numeros = re.sub(
        r"\D",
        "",
        celular
    )

    return (
        len(somente_numeros)
        == 11
    )


def dia_funcionamento(data):

    dia_especial = (
        buscar_dia_especial(data)
    )

    # Se existir uma configuração
    # especial, ela tem prioridade
    # sobre a regra normal.
    if dia_especial is not None:

        return (
            dia_especial["aberto"]
        )

    data_convertida = (
        datetime.strptime(
            data,
            "%Y-%m-%d"
        )
    )

    # Python:
    # 0 = Segunda
    # 1 = Terça
    # 2 = Quarta
    # 3 = Quinta
    # 4 = Sexta
    # 5 = Sábado
    # 6 = Domingo

    dia_semana = (
        data_convertida.weekday()
    )

    # Funcionamento normal:
    # terça-feira até sábado.
    return (
        dia_semana >= 1
        and
        dia_semana <= 5
    )


def data_dentro_do_limite(data):

    data_agendamento = (
        datetime.strptime(
            data,
            "%Y-%m-%d"
        ).date()
    )

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


def antecedencia_valida(
    data,
    horario
):

    agora = datetime.now()

    data_hora_agendamento = (
        datetime.strptime(
            f"{data} {horario}",
            "%Y-%m-%d %H:%M"
        )
    )

    antecedencia_minima = (
        agora
        + timedelta(
            minutes=30
        )
    )

    return (
        data_hora_agendamento
        >= antecedencia_minima
    )


# =========================
# PROTEÇÃO DOS AGENDAMENTOS
# =========================

def dados_agendamento_validos(agendamento):

    if not isinstance(
        agendamento,
        dict
    ):
        return False

    if (
        "data" not in agendamento
        or
        "horario" not in agendamento
        or
        "servico" not in agendamento
    ):
        return False

    if not isinstance(
        agendamento["servico"],
        dict
    ):
        return False

    if (
        "tempo"
        not in agendamento["servico"]
    ):
        return False

    tempo = (
        agendamento["servico"]["tempo"]
    )

    if (
        not isinstance(tempo, (int, float))
        or
        isinstance(tempo, bool)
        or
        tempo <= 0
    ):
        return False

    return True


def buscar_agendamentos_da_data(
    data,
    colaborador_id=None
):

    registros = buscar_agendamentos_sqlite(
        data,
        colaborador_id=colaborador_id
    )

    resultado = []

    for registro in registros:

        resultado.append({
            "id": registro["id"],
            "cliente": registro["cliente"],
            "celular": registro["celular"],
            "colaborador_id": registro["colaborador_id"],
            "colaborador_nome": registro["colaborador_nome"],
            "servico": {
                "chave": registro["servico_chave"],
                "nome": registro["servico_nome"],
                "tempo": registro["servico_tempo"],
                "valor": registro["servico_valor"]
            },
            "data": registro["data"],
            "horario": registro["horario"],
            "status": registro["status"]
        })

    return resultado


def agendamentos_incompativeis(
    data,
    aberto,
    periodos
):

    agendamentos = (
        buscar_agendamentos_da_data(
            data
        )
    )

    incompativeis = []

    for agendamento in agendamentos:

        if not aberto:
            incompativeis.append(
                agendamento
            )
            continue

        try:

            cabe = horario_cabe_em_periodos(
                agendamento["horario"],
                agendamento["servico"]["tempo"],
                periodos
            )

        except (
            ValueError,
            TypeError,
            AttributeError
        ):
            cabe = False

        if not cabe:
            incompativeis.append(
                agendamento
            )

    return incompativeis


def agendamentos_incompativeis_regra_normal(
    data
):

    agendamentos = (
        buscar_agendamentos_da_data(
            data
        )
    )

    incompativeis = []

    for agendamento in agendamentos:

        try:

            valido = horario_funcionamento_normal(
                data,
                agendamento["horario"],
                agendamento["servico"]["tempo"]
            )

        except (
            ValueError,
            TypeError,
            AttributeError
        ):
            valido = False

        if not valido:
            incompativeis.append(
                agendamento
            )

    return incompativeis


def mensagem_agendamentos_incompativeis(
    agendamentos
):

    horarios = []

    for agendamento in agendamentos:

        horario = agendamento.get(
            "horario",
            "horário desconhecido"
        )

        if horario not in horarios:
            horarios.append(horario)

    return (
        "Não é possível fazer essa alteração. "
        "Existem agendamentos que ficariam fora "
        "do novo horário de funcionamento: "
        + ", ".join(horarios)
        + "."
    )


# =========================
# PROFISSIONAIS PÚBLICOS
# =========================

@app.route(
    "/profissionais",
    methods=["GET"]
)
def profissionais_publicos():

    profissionais = (
        listar_profissionais_ativos()
    )

    return [
        {
            "id": profissional["id"],
            "nome": profissional["nome"]
        }
        for profissional in profissionais
    ]


# =========================
# REALIZAR AGENDAMENTO
# =========================

@app.route(
    "/agendar",
    methods=["POST"]
)
def agendar():

    dados = request.get_json(
        silent=True
    )

    if not isinstance(
        dados,
        dict
    ):
        return {
            "erro": "Dados inválidos!"
        }, 400

    campos_obrigatorios = [
        "nome",
        "celular",
        "servico",
        "colaborador_id",
        "data",
        "horario"
    ]

    for campo in campos_obrigatorios:

        if campo not in dados:

            return {
                "erro": "Dados incompletos!"
            }, 400


    # =========================
    # NOME E CELULAR
    # =========================

    if not nome_valido(
        dados["nome"]
    ):
        return {
            "erro": "Nome inválido!"
        }, 400

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

    if (
        not isinstance(
            chave_servico,
            str
        )
        or
        chave_servico not in SERVICOS
    ):

        return {
            "erro": "Serviço inválido!"
        }, 400

    servico = SERVICOS[
        chave_servico
    ]


    # =========================
    # PROFISSIONAL
    # =========================

    try:

        colaborador_id = int(
            dados["colaborador_id"]
        )

    except (
        ValueError,
        TypeError
    ):

        return {
            "erro": "Profissional inválido!"
        }, 400

    profissional = buscar_profissional_ativo(
        colaborador_id
    )

    if profissional is None:

        return {
            "erro": "Profissional indisponível!"
        }, 400


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

    except (
        ValueError,
        TypeError
    ):

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
                    "com pelo menos 30 minutos "
                    "de antecedência!"
                )
            }, 400

        if not horario_funcionamento(
            dados["data"],
            dados["horario"],
            servico["tempo"]
        ):

            return {
                "erro": (
                    "Horário fora do funcionamento "
                    "da barbearia!"
                )
            }, 400

    except (
        ValueError,
        TypeError
    ):

        return {
            "erro": "Horário inválido!"
        }, 400


    # =========================
    # SALVA NO SQLITE
    # =========================

    try:

        agendamento_id = (
            criar_agendamento_sqlite(
                cliente=dados["nome"].strip(),
                celular=re.sub(
                    r"\D",
                    "",
                    dados["celular"]
                ),
                colaborador_id=colaborador_id,
                servico_chave=chave_servico,
                servico_nome=servico["nome"],
                servico_tempo=servico["tempo"],
                servico_valor=servico["valor"],
                data=dados["data"],
                horario=dados["horario"]
            )
        )

    except ValueError as erro:

        return {
            "erro": str(erro)
        }, 409

    print(
        "Agendamento salvo no SQLite:",
        agendamento_id
    )

    return {
        "mensagem": (
            "Agendamento salvo com sucesso "
            f"com {profissional['nome']}!"
        ),
        "agendamento_id": agendamento_id
    }


# =========================
# HORÁRIOS DO PROFISSIONAL
# =========================

@app.route(
    "/agendamentos/<data>/<int:colaborador_id>",
    methods=["GET"]
)
def buscar_agendamentos_profissional(
    data,
    colaborador_id
):

    try:

        datetime.strptime(
            data,
            "%Y-%m-%d"
        )

    except ValueError:

        return {
            "erro": "Data inválida!"
        }, 400

    profissional = buscar_profissional_ativo(
        colaborador_id
    )

    if profissional is None:

        return {
            "erro": "Profissional indisponível!"
        }, 404

    agendamentos = buscar_agendamentos_da_data(
        data,
        colaborador_id=colaborador_id
    )

    return [
        {
            "horario": agendamento["horario"],
            "servico": {
                "tempo": agendamento["servico"]["tempo"]
            }
        }
        for agendamento in agendamentos
    ]


# Mantém a rota antiga temporariamente para
# não quebrar uma aba que ainda esteja com
# JavaScript antigo em cache.
@app.route(
    "/agendamentos/<data>",
    methods=["GET"]
)
def buscar_agendamentos(data):

    try:

        datetime.strptime(
            data,
            "%Y-%m-%d"
        )

    except ValueError:

        return {
            "erro": "Data inválida!"
        }, 400

    agendamentos = buscar_agendamentos_da_data(
        data
    )

    return [
        {
            "horario": agendamento["horario"],
            "servico": {
                "tempo": agendamento["servico"]["tempo"]
            }
        }
        for agendamento in agendamentos
    ]


# =========================
# CONSULTAR DIA ESPECIAL
# =========================

@app.route(
    "/dia-especial/<data>",
    methods=["GET"]
)
def consultar_dia_especial(data):

    dia_especial = (
        buscar_dia_especial(data)
    )

    if dia_especial is None:

        return {
            "especial": False
        }

    return {
        "especial": True,
        "aberto":
            dia_especial["aberto"],

        "periodos":
            dia_especial["periodos"]
    }


# =========================
# USUÁRIO LOGADO
# =========================

def usuario_logado():

    usuario_id = session.get(
        "usuario_id"
    )

    if usuario_id is None:
        return None

    usuario = buscar_usuario_por_id(
        usuario_id
    )

    if usuario is None:

        session.clear()
        return None

    if not usuario["ativo"]:

        session.clear()
        return None

    return usuario


# =========================
# PERMISSÕES
# =========================

def login_obrigatorio(funcao):

    @wraps(funcao)
    def verificar_login(
        *args,
        **kwargs
    ):

        if usuario_logado() is None:

            return redirect(
                url_for("login")
            )

        return funcao(
            *args,
            **kwargs
        )

    return verificar_login


def cargos_permitidos_pagina(
    *cargos
):

    def decorador(funcao):

        @wraps(funcao)
        def verificar_cargo(
            *args,
            **kwargs
        ):

            usuario = usuario_logado()

            if usuario is None:

                return redirect(
                    url_for("login")
                )

            if usuario["cargo"] not in cargos:

                return (
                    "Você não tem permissão "
                    "para acessar esta página.",
                    403
                )

            return funcao(
                *args,
                **kwargs
            )

        return verificar_cargo

    return decorador


def cargos_permitidos_api(
    *cargos
):

    def decorador(funcao):

        @wraps(funcao)
        def verificar_cargo(
            *args,
            **kwargs
        ):

            usuario = usuario_logado()

            if usuario is None:

                return {
                    "erro": (
                        "Sua sessão expirou. "
                        "Faça login novamente."
                    )
                }, 401

            if usuario["cargo"] not in cargos:

                return {
                    "erro": (
                        "Você não tem permissão "
                        "para realizar esta ação."
                    )
                }, 403

            return funcao(
                *args,
                **kwargs
            )

        return verificar_cargo

    return decorador


# =========================
# LOGIN
# =========================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    usuario = usuario_logado()

    if usuario is not None:

        return redirect(
            url_for("painel")
        )

    erro = None

    if request.method == "POST":

        nome_acesso = (
            request.form.get(
                "login",
                ""
            ).strip()
        )

        senha = request.form.get(
            "senha",
            ""
        )

        usuario = autenticar_usuario(
            nome_acesso,
            senha
        )

        if usuario is not None:

            session.clear()

            session["usuario_id"] = (
                usuario["id"]
            )

            return redirect(
                url_for("painel")
            )

        erro = (
            "Usuário ou senha inválidos."
        )

    return render_template(
        "login.html",
        erro=erro
    )


# =========================
# LOGOUT
# =========================

@app.route(
    "/logout",
    methods=["POST"]
)
@login_obrigatorio
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================
# FORMATAÇÃO PARA AS TELAS
# =========================

DIAS_SEMANA_PT = [
    "Segunda-feira",
    "Terça-feira",
    "Quarta-feira",
    "Quinta-feira",
    "Sexta-feira",
    "Sábado",
    "Domingo"
]


def formatar_celular_tela(
    celular
):

    numeros = re.sub(
        r"\D",
        "",
        str(celular)
    )

    if len(numeros) == 11:

        return (
            f"({numeros[:2]}) "
            f"{numeros[2]} "
            f"{numeros[3:7]}-"
            f"{numeros[7:]}"
        )

    return str(celular)


def preparar_agendamentos_tela(
    agendamentos
):

    resultado = []

    hoje = datetime.now().date()

    for agendamento in agendamentos:

        item = dict(
            agendamento
        )

        try:

            data_objeto = (
                datetime.strptime(
                    item["data"],
                    "%Y-%m-%d"
                ).date()
            )

            item["data_formatada"] = (
                data_objeto.strftime(
                    "%d/%m/%Y"
                )
            )

            item["dia_semana"] = (
                DIAS_SEMANA_PT[
                    data_objeto.weekday()
                ]
            )

            item["eh_hoje"] = (
                data_objeto == hoje
            )

        except (
            ValueError,
            TypeError
        ):

            item["data_formatada"] = (
                item.get(
                    "data",
                    ""
                )
            )

            item["dia_semana"] = ""
            item["eh_hoje"] = False

        item["celular_formatado"] = (
            formatar_celular_tela(
                item.get(
                    "celular",
                    ""
                )
            )
        )

        try:

            item["valor_formatado"] = (
                f"R$ "
                f"{float(item['servico_valor']):.2f}"
                .replace(".", ",")
            )

        except (
            ValueError,
            TypeError,
            KeyError
        ):

            item["valor_formatado"] = ""

        resultado.append(
            item
        )

    return resultado


# =========================
# PAINEL DO USUÁRIO
# =========================

@app.route("/painel")
@login_obrigatorio
def painel():

    usuario = usuario_logado()

    return render_template(
        "painel.html",
        usuario=usuario
    )


# =========================
# MINHA AGENDA
# =========================

@app.route("/minha-agenda")
@login_obrigatorio
def minha_agenda():

    usuario = usuario_logado()

    hoje = datetime.now().date().isoformat()

    agendamentos = (
        listar_agendamentos_colaborador(
            usuario["id"],
            data_inicial=hoje
        )
    )

    agendamentos = (
        preparar_agendamentos_tela(
            agendamentos
        )
    )

    return render_template(
        "minha_agenda.html",
        usuario=usuario,
        agendamentos=agendamentos
    )


@app.route(
    "/minha-agenda/<int:agendamento_id>/cancelar",
    methods=["POST"]
)
@login_obrigatorio
def cancelar_meu_agendamento(
    agendamento_id
):

    usuario = usuario_logado()

    agendamento = buscar_agendamento_por_id(
        agendamento_id
    )

    if agendamento is None:

        return (
            "Agendamento não encontrado.",
            404
        )

    if (
        agendamento["colaborador_id"]
        !=
        usuario["id"]
    ):

        return (
            "Você não tem permissão para cancelar este agendamento.",
            403
        )

    cancelar_agendamento_sqlite(
        agendamento_id,
        cancelado_por=usuario["id"]
    )

    return redirect(
        url_for("minha_agenda")
    )


# =========================
# AGENDAS DA EQUIPE
# =========================

@app.route("/agendas")
@cargos_permitidos_pagina(
    "dono",
    "lider"
)
def agendas_equipe():

    usuario = usuario_logado()

    hoje = datetime.now().date().isoformat()

    profissional_id = request.args.get(
        "profissional",
        default=None,
        type=int
    )

    profissionais = listar_usuarios()

    if profissional_id is not None:

        profissional_encontrado = False

        for profissional in profissionais:

            if (
                profissional["id"]
                ==
                profissional_id
            ):

                profissional_encontrado = True
                break

        if not profissional_encontrado:

            return (
                "Profissional não encontrado.",
                404
            )

    agendamentos = (
        listar_agendamentos_futuros(
            data_inicial=hoje,
            colaborador_id=profissional_id
        )
    )

    agendamentos = (
        preparar_agendamentos_tela(
            agendamentos
        )
    )

    return render_template(
        "agendas_equipe.html",
        usuario=usuario,
        profissionais=profissionais,
        profissional_id=profissional_id,
        agendamentos=agendamentos
    )


@app.route(
    "/agendas/<int:agendamento_id>/cancelar",
    methods=["POST"]
)
@cargos_permitidos_pagina(
    "dono",
    "lider"
)
def cancelar_agendamento_equipe(
    agendamento_id
):

    usuario = usuario_logado()

    agendamento = buscar_agendamento_por_id(
        agendamento_id
    )

    if agendamento is None:

        return (
            "Agendamento não encontrado.",
            404
        )

    if (
        agendamento["status"]
        !=
        "agendado"
    ):

        return redirect(
            url_for(
                "agendas_equipe"
            )
        )

    cancelar_agendamento_sqlite(
        agendamento_id,
        cancelado_por=usuario["id"]
    )

    return redirect(
        url_for(
            "agendas_equipe"
        )
    )


# =========================
# DISPONIBILIDADE PARA AGENDAMENTOS
# =========================

@app.route(
    "/equipe/<int:usuario_id>/disponibilidade",
    methods=["POST"]
)
@cargos_permitidos_pagina(
    "dono",
    "lider"
)
def alterar_disponibilidade_agendamentos(
    usuario_id
):

    usuario = buscar_usuario_por_id(
        usuario_id
    )

    if usuario is None:

        return (
            "Profissional não encontrado.",
            404
        )

    if not usuario["ativo"]:

        return (
            "Um usuário inativo não pode receber agendamentos.",
            400
        )

    novo_status = not bool(
        usuario["atende_clientes"]
    )

    definir_disponibilidade_agendamentos(
        usuario_id,
        novo_status
    )

    origem = request.form.get(
        "origem",
        "agendas"
    )

    if (
        origem == "equipe"
        and
        usuario_logado()["cargo"] == "dono"
    ):

        return redirect(
            url_for("equipe")
        )

    return redirect(
        url_for("agendas_equipe")
    )


# =========================
# EQUIPE - SOMENTE DONO
# =========================

@app.route("/equipe")
@cargos_permitidos_pagina(
    "dono"
)
def equipe():

    usuarios = listar_usuarios()

    return render_template(
        "equipe.html",
        usuarios=usuarios
    )


# =========================
# ADICIONAR COLABORADOR
# =========================

@app.route(
    "/equipe/adicionar",
    methods=["POST"]
)
@cargos_permitidos_pagina(
    "dono"
)
def adicionar_colaborador():

    nome = request.form.get(
        "nome",
        ""
    ).strip()

    login_novo = request.form.get(
        "login",
        ""
    ).strip()

    senha = request.form.get(
        "senha",
        ""
    )

    cargo = request.form.get(
        "cargo",
        "colaborador"
    )

    try:

        criar_usuario(
            nome=nome,
            login=login_novo,
            senha=senha,
            cargo=cargo,
            forcar_troca_senha=True
        )

    except ValueError as erro:

        usuarios = listar_usuarios()

        return render_template(
            "equipe.html",
            usuarios=usuarios,
            erro=str(erro)
        ), 400

    return redirect(
        url_for("equipe")
    )


# =========================
# EDITAR COLABORADOR
# =========================

@app.route(
    "/equipe/<int:usuario_id>/editar",
    methods=["POST"]
)
@cargos_permitidos_pagina(
    "dono"
)
def editar_colaborador(
    usuario_id
):

    nome = request.form.get(
        "nome",
        ""
    ).strip()

    login_novo = request.form.get(
        "login",
        ""
    ).strip()

    cargo = request.form.get(
        "cargo",
        "colaborador"
    )

    try:

        editar_usuario(
            usuario_id,
            nome,
            login_novo,
            cargo
        )

    except ValueError as erro:

        usuarios = listar_usuarios()

        return render_template(
            "equipe.html",
            usuarios=usuarios,
            erro=str(erro)
        ), 400

    return redirect(
        url_for("equipe")
    )


# =========================
# REDEFINIR SENHA
# =========================

@app.route(
    "/equipe/<int:usuario_id>/senha",
    methods=["POST"]
)
@cargos_permitidos_pagina(
    "dono"
)
def redefinir_senha_colaborador(
    usuario_id
):

    nova_senha = request.form.get(
        "nova_senha",
        ""
    )

    usuario = buscar_usuario_por_id(
        usuario_id
    )

    if usuario is None:

        return (
            "Usuário não encontrado.",
            404
        )

    if usuario["cargo"] == "dono":

        return (
            "A senha do proprietário não pode ser redefinida por esta tela.",
            403
        )

    try:

        alterar_senha(
            usuario_id,
            nova_senha,
            forcar_troca_senha=True
        )

    except ValueError as erro:

        usuarios = listar_usuarios()

        return render_template(
            "equipe.html",
            usuarios=usuarios,
            erro=str(erro)
        ), 400

    return redirect(
        url_for("equipe")
    )


# =========================
# ATIVAR / DESATIVAR
# =========================

@app.route(
    "/equipe/<int:usuario_id>/status",
    methods=["POST"]
)
@cargos_permitidos_pagina(
    "dono"
)
def alterar_status_colaborador(
    usuario_id
):

    usuario = buscar_usuario_por_id(
        usuario_id
    )

    if usuario is None:

        return (
            "Usuário não encontrado.",
            404
        )

    if usuario["cargo"] == "dono":

        return (
            "O proprietário não pode ser desativado.",
            403
        )

    novo_status = not bool(
        usuario["ativo"]
    )

    definir_usuario_ativo(
        usuario_id,
        novo_status
    )

    return redirect(
        url_for("equipe")
    )


# =========================
# PÁGINA ADMIN
# =========================

@app.route("/admin")
@cargos_permitidos_pagina(
    "dono",
    "lider"
)
def admin():

    return render_template(
        "admin.html"
    )


# =========================
# SALVAR DIA ESPECIAL
# =========================

@app.route(
    "/admin/dia-especial",
    methods=["POST"]
)
@cargos_permitidos_api(
    "dono",
    "lider"
)
def salvar_dia_especial():

    dados = request.get_json(
        silent=True
    )

    if not isinstance(
        dados,
        dict
    ):
        return {
            "erro": "Dados inválidos!"
        }, 400

    campos_obrigatorios = [
        "data",
        "aberto",
        "periodos"
    ]

    for campo in campos_obrigatorios:

        if campo not in dados:
            return {
                "erro": "Dados incompletos!"
            }, 400

    # =========================
    # VALIDA DATA
    # =========================

    if not isinstance(
        dados["data"],
        str
    ):
        return {
            "erro": "Data inválida!"
        }, 400

    try:

        datetime.strptime(
            dados["data"],
            "%Y-%m-%d"
        )

    except ValueError:

        return {
            "erro": "Data inválida!"
        }, 400

    # =========================
    # VALIDA ABERTO / FECHADO
    # =========================

    if not isinstance(
        dados["aberto"],
        bool
    ):
        return {
            "erro": "Funcionamento inválido!"
        }, 400

    # =========================
    # VALIDA PERÍODOS
    # =========================

    if dados["aberto"]:

        if not periodos_validos(
            dados["periodos"]
        ):
            return {
                "erro": (
                    "Períodos de funcionamento "
                    "inválidos!"
                )
            }, 400

    else:
        dados["periodos"] = []

    # =========================
    # PROTEGE AGENDAMENTOS
    # =========================

    incompativeis = (
        agendamentos_incompativeis(
            dados["data"],
            dados["aberto"],
            dados["periodos"]
        )
    )

    if incompativeis:

        return {
            "erro":
                mensagem_agendamentos_incompativeis(
                    incompativeis
                )
        }, 409

    # =========================
    # BUSCA DIA EXISTENTE
    # =========================

    dias_especiais = (
        carregar_dias_especiais()
    )

    dia_existente = None

    for dia in dias_especiais:

        if dia["data"] == dados["data"]:
            dia_existente = dia
            break

    novo_dia = {
        "data": dados["data"],
        "aberto": dados["aberto"],
        "periodos": dados["periodos"]
    }

    if dia_existente is not None:
        dia_existente["aberto"] = (
            novo_dia["aberto"]
        )
        dia_existente["periodos"] = (
            novo_dia["periodos"]
        )

    else:
        dias_especiais.append(
            novo_dia
        )

    salvar_dias_especiais(
        dias_especiais
    )

    return {
        "mensagem": (
            "Dia especial salvo "
            "com sucesso!"
        )
    }


# =========================
# REMOVER DIA ESPECIAL
# =========================

@app.route(
    "/admin/dia-especial/<data>",
    methods=["DELETE"]
)
@cargos_permitidos_api(
    "dono",
    "lider"
)
def remover_dia_especial(data):

    try:

        datetime.strptime(
            data,
            "%Y-%m-%d"
        )

    except ValueError:

        return {
            "erro": "Data inválida!"
        }, 400

    dias_especiais = (
        carregar_dias_especiais()
    )

    dia_encontrado = None

    for dia in dias_especiais:

        if dia["data"] == data:
            dia_encontrado = dia
            break

    if dia_encontrado is None:

        return {
            "erro": (
                "Esse dia especial "
                "não existe!"
            )
        }, 404

    # Remover a exceção faz a data
    # voltar ao funcionamento normal.
    # Antes disso, garante que nenhum
    # cliente ficará em horário inválido.
    incompativeis = (
        agendamentos_incompativeis_regra_normal(
            data
        )
    )

    if incompativeis:

        horarios = []

        for agendamento in incompativeis:
            horario = agendamento["horario"]

            if horario not in horarios:
                horarios.append(horario)

        return {
            "erro": (
                "Não é possível remover esse dia "
                "especial porque existem agendamentos "
                "que não cabem no funcionamento normal: "
                + ", ".join(horarios)
                + "."
            )
        }, 409

    novos_dias = []

    for dia in dias_especiais:

        if dia["data"] == data:
            continue

        novos_dias.append(dia)

    salvar_dias_especiais(
        novos_dias
    )

    return {
        "mensagem": (
            "Dia especial removido "
            "com sucesso!"
        )
    }


# =========================
# INICIAR FLASK
# =========================

if __name__ == "__main__":

    app.run(
        debug=True
    )