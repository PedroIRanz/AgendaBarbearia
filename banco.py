import os
import sqlite3
import hashlib
import hmac
import secrets
from getpass import getpass


# =========================
# CAMINHO DO BANCO
# =========================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

CAMINHO_BANCO = os.path.join(
    BASE_DIR,
    "barbearia.db"
)


# =========================
# CARGOS
# =========================

CARGOS_VALIDOS = (
    "dono",
    "lider",
    "colaborador"
)


# =========================
# SENHAS
# =========================

ITERACOES_HASH = 600_000


def gerar_hash_senha(senha):

    if not isinstance(senha, str):

        raise ValueError(
            "Senha inválida."
        )

    salt = secrets.token_bytes(16)

    hash_bytes = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt,
        ITERACOES_HASH
    )

    return (
        f"pbkdf2_sha256"
        f"${ITERACOES_HASH}"
        f"${salt.hex()}"
        f"${hash_bytes.hex()}"
    )


def verificar_senha(
    senha,
    senha_hash
):

    try:

        algoritmo, iteracoes, salt_hex, hash_hex = (
            senha_hash.split("$", 3)
        )

        if algoritmo != "pbkdf2_sha256":
            return False

        salt = bytes.fromhex(
            salt_hex
        )

        hash_esperado = bytes.fromhex(
            hash_hex
        )

        hash_recebido = hashlib.pbkdf2_hmac(
            "sha256",
            senha.encode("utf-8"),
            salt,
            int(iteracoes)
        )

        return hmac.compare_digest(
            hash_recebido,
            hash_esperado
        )

    except (
        ValueError,
        TypeError,
        AttributeError
    ):

        return False


# =========================
# CONEXÃO
# =========================

def conectar_banco():

    conexao = sqlite3.connect(
        CAMINHO_BANCO
    )

    conexao.row_factory = (
        sqlite3.Row
    )

    conexao.execute(
        "PRAGMA foreign_keys = ON"
    )

    return conexao


# =========================
# CRIAR TABELAS
# =========================

def criar_tabelas():

    conexao = conectar_banco()

    try:

        conexao.executescript(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                nome TEXT NOT NULL,

                login TEXT NOT NULL
                    UNIQUE COLLATE NOCASE,

                senha_hash TEXT NOT NULL,

                cargo TEXT NOT NULL
                    CHECK (
                        cargo IN (
                            'dono',
                            'lider',
                            'colaborador'
                        )
                    ),

                ativo INTEGER NOT NULL
                    DEFAULT 1
                    CHECK (
                        ativo IN (0, 1)
                    ),

                atende_clientes INTEGER NOT NULL
                    DEFAULT 1
                    CHECK (
                        atende_clientes IN (0, 1)
                    ),

                forcar_troca_senha INTEGER NOT NULL
                    DEFAULT 0
                    CHECK (
                        forcar_troca_senha IN (0, 1)
                    ),

                criado_em TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                atualizado_em TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            );


            CREATE INDEX IF NOT EXISTS
                idx_usuarios_cargo
            ON usuarios(cargo);


            CREATE INDEX IF NOT EXISTS
                idx_usuarios_ativo
            ON usuarios(ativo);


            CREATE TABLE IF NOT EXISTS agendamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                cliente TEXT NOT NULL,
                celular TEXT NOT NULL,

                colaborador_id INTEGER NOT NULL,

                servico_chave TEXT NOT NULL,
                servico_nome TEXT NOT NULL,
                servico_tempo INTEGER NOT NULL
                    CHECK (servico_tempo > 0),
                servico_valor REAL NOT NULL
                    CHECK (servico_valor >= 0),

                data TEXT NOT NULL,
                horario TEXT NOT NULL,

                status TEXT NOT NULL
                    DEFAULT 'agendado'
                    CHECK (
                        status IN (
                            'agendado',
                            'cancelado'
                        )
                    ),

                criado_em TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                cancelado_em TEXT,
                cancelado_por INTEGER,

                FOREIGN KEY (colaborador_id)
                    REFERENCES usuarios(id),

                FOREIGN KEY (cancelado_por)
                    REFERENCES usuarios(id)
            );


            CREATE INDEX IF NOT EXISTS
                idx_agendamentos_profissional_data
            ON agendamentos(
                colaborador_id,
                data,
                status
            );


            CREATE INDEX IF NOT EXISTS
                idx_agendamentos_data
            ON agendamentos(
                data,
                status
            );


            CREATE TABLE IF NOT EXISTS migracoes (
                chave TEXT PRIMARY KEY,
                executada_em TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        # Migração automática para bancos
        # criados em versões anteriores.
        colunas_usuarios = {
            coluna["name"]
            for coluna in conexao.execute(
                "PRAGMA table_info(usuarios)"
            ).fetchall()
        }

        if (
            "atende_clientes"
            not in colunas_usuarios
        ):

            conexao.execute(
                """
                ALTER TABLE usuarios
                ADD COLUMN atende_clientes INTEGER NOT NULL
                    DEFAULT 1
                    CHECK (
                        atende_clientes IN (0, 1)
                    )
                """
            )

        conexao.execute(
            """
            CREATE INDEX IF NOT EXISTS
                idx_usuarios_atende_clientes
            ON usuarios(atende_clientes)
            """
        )

        conexao.commit()

    finally:

        conexao.close()


# =========================
# LOGIN
# =========================

def normalizar_login(login):

    if not isinstance(
        login,
        str
    ):
        return ""

    return login.strip().lower()


# =========================
# BUSCAR USUÁRIO
# =========================

def buscar_usuario_por_id(
    usuario_id
):

    conexao = conectar_banco()

    try:

        return conexao.execute(
            """
            SELECT
                id,
                nome,
                login,
                senha_hash,
                cargo,
                ativo,
                atende_clientes,
                forcar_troca_senha,
                criado_em,
                atualizado_em
            FROM usuarios
            WHERE id = ?
            """,
            (usuario_id,)
        ).fetchone()

    finally:

        conexao.close()


def buscar_usuario_por_login(
    login
):

    login = normalizar_login(
        login
    )

    if not login:
        return None

    conexao = conectar_banco()

    try:

        return conexao.execute(
            """
            SELECT
                id,
                nome,
                login,
                senha_hash,
                cargo,
                ativo,
                atende_clientes,
                forcar_troca_senha,
                criado_em,
                atualizado_em
            FROM usuarios
            WHERE login = ?
            """,
            (login,)
        ).fetchone()

    finally:

        conexao.close()


# =========================
# LISTAR USUÁRIOS
# =========================

def listar_usuarios(
    somente_ativos=False
):

    conexao = conectar_banco()

    try:

        if somente_ativos:

            return conexao.execute(
                """
                SELECT
                    id,
                    nome,
                    login,
                    cargo,
                    ativo,
                    atende_clientes,
                    forcar_troca_senha,
                    criado_em,
                    atualizado_em
                FROM usuarios
                WHERE ativo = 1
                ORDER BY nome COLLATE NOCASE
                """
            ).fetchall()

        return conexao.execute(
            """
            SELECT
                id,
                nome,
                login,
                cargo,
                ativo,
                atende_clientes,
                forcar_troca_senha,
                criado_em,
                atualizado_em
            FROM usuarios
            ORDER BY nome COLLATE NOCASE
            """
        ).fetchall()

    finally:

        conexao.close()


# =========================
# CRIAR USUÁRIO
# =========================

def criar_usuario(
    nome,
    login,
    senha,
    cargo="colaborador",
    forcar_troca_senha=False
):

    nome = str(nome).strip()

    login = normalizar_login(
        login
    )

    if len(nome) < 2:

        raise ValueError(
            "Nome inválido."
        )

    if len(login) < 3:

        raise ValueError(
            "O login precisa ter pelo menos 3 caracteres."
        )

    if cargo not in CARGOS_VALIDOS:

        raise ValueError(
            "Cargo inválido."
        )

    if not isinstance(
        senha,
        str
    ) or len(senha) < 8:

        raise ValueError(
            "A senha precisa ter pelo menos 8 caracteres."
        )

    senha_hash = gerar_hash_senha(
        senha
    )

    conexao = conectar_banco()

    try:

        cursor = conexao.execute(
            """
            INSERT INTO usuarios (
                nome,
                login,
                senha_hash,
                cargo,
                ativo,
                forcar_troca_senha
            )
            VALUES (?, ?, ?, ?, 1, ?)
            """,
            (
                nome,
                login,
                senha_hash,
                cargo,
                int(
                    bool(
                        forcar_troca_senha
                    )
                )
            )
        )

        conexao.commit()

        return cursor.lastrowid

    except sqlite3.IntegrityError as erro:

        if "usuarios.login" in str(
            erro
        ):

            raise ValueError(
                "Esse login já está em uso."
            ) from erro

        raise

    finally:

        conexao.close()


# =========================
# AUTENTICAR USUÁRIO
# =========================

def autenticar_usuario(
    login,
    senha
):

    usuario = (
        buscar_usuario_por_login(
            login
        )
    )

    if usuario is None:
        return None

    if not usuario["ativo"]:
        return None

    if not verificar_senha(
        senha,
        usuario["senha_hash"]
    ):
        return None

    return usuario


# =========================
# ALTERAR SENHA
# =========================

def alterar_senha(
    usuario_id,
    nova_senha,
    forcar_troca_senha=False
):

    if not isinstance(
        nova_senha,
        str
    ) or len(nova_senha) < 8:

        raise ValueError(
            "A senha precisa ter pelo menos 8 caracteres."
        )

    nova_hash = gerar_hash_senha(
        nova_senha
    )

    conexao = conectar_banco()

    try:

        cursor = conexao.execute(
            """
            UPDATE usuarios
            SET
                senha_hash = ?,
                forcar_troca_senha = ?,
                atualizado_em = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                nova_hash,
                int(
                    bool(
                        forcar_troca_senha
                    )
                ),
                usuario_id
            )
        )

        conexao.commit()

        return (
            cursor.rowcount == 1
        )

    finally:

        conexao.close()


# =========================
# ALTERAR CARGO
# =========================

def alterar_cargo(
    usuario_id,
    novo_cargo
):

    if novo_cargo not in (
        CARGOS_VALIDOS
    ):

        raise ValueError(
            "Cargo inválido."
        )

    conexao = conectar_banco()

    try:

        cursor = conexao.execute(
            """
            UPDATE usuarios
            SET
                cargo = ?,
                atualizado_em = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                novo_cargo,
                usuario_id
            )
        )

        conexao.commit()

        return (
            cursor.rowcount == 1
        )

    finally:

        conexao.close()


# =========================
# EDITAR USUÁRIO
# =========================

def editar_usuario(
    usuario_id,
    nome,
    login,
    cargo
):

    nome = str(nome).strip()

    login = normalizar_login(
        login
    )

    if len(nome) < 2:

        raise ValueError(
            "Nome inválido."
        )

    if len(login) < 3:

        raise ValueError(
            "O login precisa ter pelo menos 3 caracteres."
        )

    if cargo not in (
        "lider",
        "colaborador"
    ):

        raise ValueError(
            "Cargo inválido."
        )

    conexao = conectar_banco()

    try:

        usuario = conexao.execute(
            """
            SELECT
                id,
                cargo
            FROM usuarios
            WHERE id = ?
            """,
            (usuario_id,)
        ).fetchone()

        if usuario is None:

            raise ValueError(
                "Usuário não encontrado."
            )

        if usuario["cargo"] == "dono":

            raise ValueError(
                "O proprietário não pode ser alterado por esta tela."
            )

        try:

            cursor = conexao.execute(
                """
                UPDATE usuarios
                SET
                    nome = ?,
                    login = ?,
                    cargo = ?,
                    atualizado_em = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    nome,
                    login,
                    cargo,
                    usuario_id
                )
            )

            conexao.commit()

            return (
                cursor.rowcount == 1
            )

        except sqlite3.IntegrityError as erro:

            if "usuarios.login" in str(
                erro
            ):

                raise ValueError(
                    "Esse login já está em uso."
                ) from erro

            raise

    finally:

        conexao.close()


# =========================
# ATIVAR / DESATIVAR
# =========================

def definir_usuario_ativo(
    usuario_id,
    ativo
):

    conexao = conectar_banco()

    try:

        cursor = conexao.execute(
            """
            UPDATE usuarios
            SET
                ativo = ?,
                atualizado_em = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                int(bool(ativo)),
                usuario_id
            )
        )

        conexao.commit()

        return (
            cursor.rowcount == 1
        )

    finally:

        conexao.close()


# =========================
# PROFISSIONAIS
# =========================

def listar_profissionais_ativos():

    conexao = conectar_banco()

    try:

        return conexao.execute(
            """
            SELECT
                id,
                nome,
                cargo,
                atende_clientes
            FROM usuarios
            WHERE
                ativo = 1
                AND atende_clientes = 1
            ORDER BY
                CASE cargo
                    WHEN 'dono' THEN 1
                    WHEN 'lider' THEN 2
                    ELSE 3
                END,
                nome COLLATE NOCASE
            """
        ).fetchall()

    finally:

        conexao.close()


def buscar_profissional_ativo(
    usuario_id
):

    conexao = conectar_banco()

    try:

        return conexao.execute(
            """
            SELECT
                id,
                nome,
                cargo,
                ativo,
                atende_clientes
            FROM usuarios
            WHERE
                id = ?
                AND ativo = 1
                AND atende_clientes = 1
            """,
            (usuario_id,)
        ).fetchone()

    finally:

        conexao.close()


def definir_disponibilidade_agendamentos(
    usuario_id,
    atende_clientes
):

    conexao = conectar_banco()

    try:

        cursor = conexao.execute(
            """
            UPDATE usuarios
            SET
                atende_clientes = ?,
                atualizado_em = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                int(bool(atende_clientes)),
                usuario_id
            )
        )

        conexao.commit()

        return (
            cursor.rowcount == 1
        )

    finally:

        conexao.close()


# =========================
# AGENDAMENTOS SQLITE
# =========================

def horario_para_minutos_banco(
    horario
):

    hora, minuto = horario.split(":")

    return (
        int(hora) * 60
        + int(minuto)
    )


def buscar_agendamentos_sqlite(
    data,
    colaborador_id=None,
    incluir_cancelados=False
):

    conexao = conectar_banco()

    try:

        consulta = """
            SELECT
                a.id,
                a.cliente,
                a.celular,
                a.colaborador_id,
                u.nome AS colaborador_nome,
                a.servico_chave,
                a.servico_nome,
                a.servico_tempo,
                a.servico_valor,
                a.data,
                a.horario,
                a.status,
                a.criado_em,
                a.cancelado_em,
                a.cancelado_por
            FROM agendamentos AS a
            JOIN usuarios AS u
                ON u.id = a.colaborador_id
            WHERE a.data = ?
        """

        parametros = [data]

        if colaborador_id is not None:

            consulta += """
                AND a.colaborador_id = ?
            """

            parametros.append(
                colaborador_id
            )

        if not incluir_cancelados:

            consulta += """
                AND a.status = 'agendado'
            """

        consulta += """
            ORDER BY
                a.horario,
                u.nome COLLATE NOCASE
        """

        return conexao.execute(
            consulta,
            tuple(parametros)
        ).fetchall()

    finally:

        conexao.close()


def listar_agendamentos_colaborador(
    colaborador_id,
    data_inicial=None,
    incluir_cancelados=False
):

    conexao = conectar_banco()

    try:

        consulta = """
            SELECT
                a.id,
                a.cliente,
                a.celular,
                a.colaborador_id,
                u.nome AS colaborador_nome,
                a.servico_chave,
                a.servico_nome,
                a.servico_tempo,
                a.servico_valor,
                a.data,
                a.horario,
                a.status,
                a.criado_em,
                a.cancelado_em,
                a.cancelado_por
            FROM agendamentos AS a
            JOIN usuarios AS u
                ON u.id = a.colaborador_id
            WHERE a.colaborador_id = ?
        """

        parametros = [
            colaborador_id
        ]

        if data_inicial is not None:

            consulta += """
                AND a.data >= ?
            """

            parametros.append(
                data_inicial
            )

        if not incluir_cancelados:

            consulta += """
                AND a.status = 'agendado'
            """

        consulta += """
            ORDER BY
                a.data,
                a.horario
        """

        return conexao.execute(
            consulta,
            tuple(parametros)
        ).fetchall()

    finally:

        conexao.close()


def listar_agendamentos_futuros(
    data_inicial,
    colaborador_id=None,
    incluir_cancelados=False
):

    conexao = conectar_banco()

    try:

        consulta = """
            SELECT
                a.id,
                a.cliente,
                a.celular,
                a.colaborador_id,
                u.nome AS colaborador_nome,
                u.ativo AS colaborador_ativo,
                a.servico_chave,
                a.servico_nome,
                a.servico_tempo,
                a.servico_valor,
                a.data,
                a.horario,
                a.status,
                a.criado_em,
                a.cancelado_em,
                a.cancelado_por
            FROM agendamentos AS a
            JOIN usuarios AS u
                ON u.id = a.colaborador_id
            WHERE a.data >= ?
        """

        parametros = [
            data_inicial
        ]

        if colaborador_id is not None:

            consulta += """
                AND a.colaborador_id = ?
            """

            parametros.append(
                colaborador_id
            )

        if not incluir_cancelados:

            consulta += """
                AND a.status = 'agendado'
            """

        consulta += """
            ORDER BY
                a.data,
                a.horario,
                u.nome COLLATE NOCASE
        """

        return conexao.execute(
            consulta,
            tuple(parametros)
        ).fetchall()

    finally:

        conexao.close()


def buscar_agendamento_por_id(
    agendamento_id
):

    conexao = conectar_banco()

    try:

        return conexao.execute(
            """
            SELECT
                a.id,
                a.cliente,
                a.celular,
                a.colaborador_id,
                u.nome AS colaborador_nome,
                a.servico_chave,
                a.servico_nome,
                a.servico_tempo,
                a.servico_valor,
                a.data,
                a.horario,
                a.status,
                a.criado_em,
                a.cancelado_em,
                a.cancelado_por
            FROM agendamentos AS a
            JOIN usuarios AS u
                ON u.id = a.colaborador_id
            WHERE a.id = ?
            """,
            (agendamento_id,)
        ).fetchone()

    finally:

        conexao.close()


def criar_agendamento_sqlite(
    cliente,
    celular,
    colaborador_id,
    servico_chave,
    servico_nome,
    servico_tempo,
    servico_valor,
    data,
    horario
):

    inicio_novo = (
        horario_para_minutos_banco(
            horario
        )
    )

    fim_novo = (
        inicio_novo
        + servico_tempo
    )

    conexao = conectar_banco()

    try:

        # Bloqueia escrita concorrente durante
        # a checagem + criação do horário.
        conexao.execute(
            "BEGIN IMMEDIATE"
        )

        profissional = conexao.execute(
            """
            SELECT
                id,
                ativo
            FROM usuarios
            WHERE id = ?
            """,
            (colaborador_id,)
        ).fetchone()

        if (
            profissional is None
            or
            not profissional["ativo"]
        ):

            raise ValueError(
                "Profissional indisponível."
            )

        existentes = conexao.execute(
            """
            SELECT
                horario,
                servico_tempo
            FROM agendamentos
            WHERE
                colaborador_id = ?
                AND data = ?
                AND status = 'agendado'
            """,
            (
                colaborador_id,
                data
            )
        ).fetchall()

        for existente in existentes:

            inicio_existente = (
                horario_para_minutos_banco(
                    existente["horario"]
                )
            )

            fim_existente = (
                inicio_existente
                + existente["servico_tempo"]
            )

            if (
                inicio_novo < fim_existente
                and
                fim_novo > inicio_existente
            ):

                raise ValueError(
                    "Esse horário já está ocupado para esse profissional."
                )

        cursor = conexao.execute(
            """
            INSERT INTO agendamentos (
                cliente,
                celular,
                colaborador_id,
                servico_chave,
                servico_nome,
                servico_tempo,
                servico_valor,
                data,
                horario,
                status
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, 'agendado'
            )
            """,
            (
                cliente,
                celular,
                colaborador_id,
                servico_chave,
                servico_nome,
                servico_tempo,
                servico_valor,
                data,
                horario
            )
        )

        conexao.commit()

        return cursor.lastrowid

    except Exception:

        conexao.rollback()
        raise

    finally:

        conexao.close()


def cancelar_agendamento_sqlite(
    agendamento_id,
    cancelado_por
):

    conexao = conectar_banco()

    try:

        cursor = conexao.execute(
            """
            UPDATE agendamentos
            SET
                status = 'cancelado',
                cancelado_em = CURRENT_TIMESTAMP,
                cancelado_por = ?
            WHERE
                id = ?
                AND status = 'agendado'
            """,
            (
                cancelado_por,
                agendamento_id
            )
        )

        conexao.commit()

        return (
            cursor.rowcount == 1
        )

    finally:

        conexao.close()


# =========================
# MIGRAÇÃO DO JSON ANTIGO
# =========================

def migrar_agendamentos_legados(
    registros,
    colaborador_id,
    chave_migracao="agendamentos_json_v1"
):

    conexao = conectar_banco()

    try:

        conexao.execute(
            "BEGIN IMMEDIATE"
        )

        ja_executada = conexao.execute(
            """
            SELECT 1
            FROM migracoes
            WHERE chave = ?
            """,
            (chave_migracao,)
        ).fetchone()

        if ja_executada is not None:

            conexao.rollback()
            return 0

        quantidade = 0

        for registro in registros:

            conexao.execute(
                """
                INSERT INTO agendamentos (
                    cliente,
                    celular,
                    colaborador_id,
                    servico_chave,
                    servico_nome,
                    servico_tempo,
                    servico_valor,
                    data,
                    horario,
                    status
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, 'agendado'
                )
                """,
                (
                    registro["cliente"],
                    registro["celular"],
                    colaborador_id,
                    registro["servico_chave"],
                    registro["servico_nome"],
                    registro["servico_tempo"],
                    registro["servico_valor"],
                    registro["data"],
                    registro["horario"]
                )
            )

            quantidade += 1

        conexao.execute(
            """
            INSERT INTO migracoes (
                chave
            )
            VALUES (?)
            """,
            (chave_migracao,)
        )

        conexao.commit()

        return quantidade

    except Exception:

        conexao.rollback()
        raise

    finally:

        conexao.close()


# =========================
# PRIMEIRO DONO
# =========================

def existe_dono():

    conexao = conectar_banco()

    try:

        resultado = conexao.execute(
            """
            SELECT 1
            FROM usuarios
            WHERE
                cargo = 'dono'
                AND ativo = 1
            LIMIT 1
            """
        ).fetchone()

        return (
            resultado is not None
        )

    finally:

        conexao.close()


def criar_primeiro_dono():

    criar_tabelas()

    if existe_dono():

        print(
            "Já existe um proprietário ativo cadastrado."
        )

        return

    print()
    print(
        "=== CADASTRO DO PRIMEIRO PROPRIETÁRIO ==="
    )
    print()

    nome = input(
        "Nome do proprietário: "
    ).strip()

    login = input(
        "Login: "
    ).strip()

    senha = getpass(
        "Senha: "
    )

    confirmar_senha = getpass(
        "Confirme a senha: "
    )

    if senha != confirmar_senha:

        print()
        print(
            "As senhas não são iguais."
        )

        return

    try:

        usuario_id = criar_usuario(
            nome=nome,
            login=login,
            senha=senha,
            cargo="dono"
        )

    except ValueError as erro:

        print()
        print(
            f"Erro: {erro}"
        )

        return

    print()
    print(
        "Proprietário criado com sucesso."
    )
    print(
        f"ID do usuário: {usuario_id}"
    )


# =========================
# EXECUÇÃO DIRETA
# =========================

if __name__ == "__main__":

    criar_primeiro_dono()
