"""
db.py
Camada simples de acesso ao PostgreSQL (instância local).
Lê a connection string da variável de ambiente DATABASE_URL (arquivo .env).

Usa psycopg2 quando disponível. Se o Windows bloquear a DLL (Controle de
Aplicativo), cai automaticamente para o driver pg8000 (Python puro).
"""

import os
from urllib.parse import unquote, urlparse

from dotenv import load_dotenv

# Carrega o .env que fica na raiz do projeto (um nível acima de /src)
_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_RAIZ, ".env"))

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

try:
    import psycopg2
    import psycopg2.extras

    DatabaseError = psycopg2.Error
    _DRIVER = "psycopg2"
except Exception:
    import pg8000.dbapi as pg8000

    DatabaseError = pg8000.Error
    _DRIVER = "pg8000"


# Exceção customizada para problemas de configuração do .env.
# A aplicação captura isso e mostra uma página amigável.
class ConfiguracaoBancoInvalida(Exception):
    pass


def _validar_url():
    """Checa se a DATABASE_URL foi preenchida de verdade (sem placeholders)."""
    if not DATABASE_URL:
        raise ConfiguracaoBancoInvalida(
            "A variável DATABASE_URL não foi definida. "
            "Copie o arquivo .env.example para .env e preencha a "
            "connection string do seu PostgreSQL."
        )
    marcadores = ["YOUR-PASSWORD", "SUA_SENHA", "SUA-SENHA"]
    if any(m in DATABASE_URL for m in marcadores):
        raise ConfiguracaoBancoInvalida(
            "A DATABASE_URL ainda contém valores de exemplo. "
            "Abra o arquivo .env e troque SUA_SENHA pela senha real "
            "do usuário postgres."
        )


def _conectar_pg8000(url):
    parsed = urlparse(url)
    database = unquote(parsed.path.lstrip("/"))
    if "?" in database:
        database = database.split("?", 1)[0]
    return pg8000.connect(
        user=unquote(parsed.username or "postgres"),
        password=unquote(parsed.password or ""),
        host=parsed.hostname or "localhost",
        port=parsed.port or 5432,
        database=database,
    )


def _traduzir_erro_conexao(e):
    msg = str(e).strip()
    if "could not translate host name" in msg or "Name or service not known" in msg:
        raise ConfiguracaoBancoInvalida(
            "Não consegui resolver o host do banco. "
            "Verifique a parte 'host' da DATABASE_URL no .env — "
            "para PostgreSQL instalado na própria máquina, use 'localhost'."
        ) from e
    if "Connection refused" in msg or "could not connect to server" in msg:
        raise ConfiguracaoBancoInvalida(
            "O servidor PostgreSQL não está respondendo. "
            "Confirme que o serviço do PostgreSQL está rodando "
            "(no Windows: Serviços > postgresql-x64-XX > Iniciar)."
        ) from e
    if "does not exist" in msg and "database" in msg:
        raise ConfiguracaoBancoInvalida(
            "O banco informado na DATABASE_URL não existe. "
            "Rode: psql -U postgres -c \"CREATE DATABASE mercado_pro;\""
        ) from e
    if "password authentication failed" in msg:
        raise ConfiguracaoBancoInvalida(
            "Senha incorreta para o usuário do PostgreSQL. "
            "Confira a senha no arquivo .env."
        ) from e
    raise ConfiguracaoBancoInvalida(
        f"Erro ao conectar no banco: {msg}"
    ) from e


def get_connection():
    """Abre uma nova conexão com o banco. O chamador é responsável por fechar."""
    _validar_url()
    try:
        if _DRIVER == "psycopg2":
            return psycopg2.connect(DATABASE_URL)
        return _conectar_pg8000(DATABASE_URL)
    except Exception as e:
        _traduzir_erro_conexao(e)


def _como_dicts(cur, rows):
    if not cur.description:
        return []
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in rows]


def _cursor(conn):
    if _DRIVER == "psycopg2":
        return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    return conn.cursor()


def fetch_all(sql, params=None):
    """Executa SELECT e devolve lista de dicts."""
    conn = get_connection()
    try:
        cur = _cursor(conn)
        try:
            cur.execute(sql, params or ())
            rows = cur.fetchall()
            if _DRIVER == "psycopg2":
                return rows
            return _como_dicts(cur, rows)
        finally:
            cur.close()
    finally:
        conn.close()


def fetch_one(sql, params=None):
    """Executa SELECT e devolve um dict (ou None)."""
    conn = get_connection()
    try:
        cur = _cursor(conn)
        try:
            cur.execute(sql, params or ())
            row = cur.fetchone()
            if row is None:
                return None
            if _DRIVER == "psycopg2":
                return row
            return _como_dicts(cur, [row])[0]
        finally:
            cur.close()
    finally:
        conn.close()


def execute(sql, params=None):
    """Executa INSERT/UPDATE/DELETE com commit."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        try:
            cur.execute(sql, params or ())
        finally:
            cur.close()
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def call_procedure(nome_proc, params):
    """
    Chama uma PROCEDURE do PostgreSQL (CALL ...).
    A aplicação controla commit/rollback.
    Se a procedure disparar RAISE EXCEPTION, a mensagem é propagada.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        try:
            placeholders = ", ".join(["%s"] * len(params))
            sql = f"CALL {nome_proc}({placeholders})"
            cur.execute(sql, params)
        finally:
            cur.close()
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
