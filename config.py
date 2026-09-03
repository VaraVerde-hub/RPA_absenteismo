"""
Configurações centrais do projeto de Absenteísmo.

Todas as credenciais sensíveis (banco de dados e email) são lidas de
variáveis de ambiente — nunca deixe senhas escritas direto no código.

Como definir as variáveis de ambiente:

Linux/Mac (terminal):
    export DB_CONNECTION_STRING="postgresql+psycopg2://usuario:senha@host:5432/nome_banco"
    export SMTP_HOST="smtp.gmail.com"
    export SMTP_PORT="587"
    export SMTP_USER="seuemail@empresa.com"
    export SMTP_PASSWORD="sua_senha_de_app"
    export EMAIL_DESTINATARIOS="gestor1@empresa.com,gestor2@empresa.com"

Windows (PowerShell):
    $env:DB_CONNECTION_STRING="postgresql+psycopg2://usuario:senha@host:5432/nome_banco"
    (idem para as demais)

Ou, mais simples: crie um arquivo ".env" na raiz do projeto (veja o
README) e use "python-dotenv" para carregá-lo automaticamente.
"""

import os

from sqlalchemy import create_engine
# ---------------------------------------------------------------------
# BANCO DE DADOS
# ---------------------------------------------------------------------
# String de conexão SQLAlchemy. Exemplos:
#   PostgreSQL: "postgresql+psycopg2://usuario:senha@host:5432/banco"
#   MySQL:      "mysql+pymysql://usuario:senha@host:3306/banco"
#   SQL Server: "mssql+pyodbc://usuario:senha@host/banco?driver=ODBC+Driver+17+for+SQL+Server"



server = "VARAVERDE_DELL"
database = "db_catraca"
username = "sa"
password = "123456789"

connection_string = (
    f"mssql+pyodbc://{username}:{password}@{server}/{database}"
    "?driver=ODBC+Driver+18+for+SQL+Server"
    "&TrustServerCertificate=yes"
)

engine = create_engine(connection_string)


# ---------------------------------------------------------------------
# NOMES DE TABELAS E COLUNAS
# ---------------------------------------------------------------------
# AJUSTE ESTES NOMES para bater com a sua base real de dados.
# O restante do código usa só estes nomes, então mudar aqui é suficiente
# na maioria dos casos.

TABELA_FUNCIONARIOS = "[db_catraca].[dbo].[Funcionarios]"
COL_FUNC_ID = "[IdFuncionario]"
COL_FUNC_NOME = "[Nome]"
COL_FUNC_CARGO = "[Cargo]"
COL_FUNC_SETOR = "[Setor]"
COL_FUNC_HORARIO_ENTRADA_ESPERADO = "[JornadaInicio]"  # ex: 08:00:00
COL_FUNC_HORARIO_SAIDA_ESPERADO = "[JornadaFim]"       # ex: 18:00:00

TABELA_REGISTROS = "[db_catraca].[dbo].[registros_ponto]"
COL_REG_ID = "[funcionario_id]"
COL_REG_DATA = "[data]"
COL_REG_HORA_ENTRADA = "[hora_entrada]"
COL_REG_HORA_SAIDA = "[hora_saida]"


# ---------------------------------------------------------------------
# REGRAS DE ABSENTEÍSMO
# ---------------------------------------------------------------------
# Tolerância em minutos antes de considerar atraso/saída antecipada.
TOLERANCIA_ATRASO_MINUTOS = 10
TOLERANCIA_SAIDA_ANTECIPADA_MINUTOS = 10

# Período do relatório: quantos dias corridos para trás olhar
# (ex: 1 = só o dia anterior, 7 = última semana)
PERIODO_RELATORIO_DIAS = 1

# ---------------------------------------------------------------------
# EMAIL
# ---------------------------------------------------------------------
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "augustob2246@gmail.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "dshmiszzxlkjnjji")

# Lista de destinatários separada por vírgula na variável de ambiente
EMAIL_DESTINATARIOS = [
    e.strip() for e in os.environ.get("EMAIL_DESTINATARIOS", "augustob2246@gmail.com").split(",") if e.strip()
]

EMAIL_ASSUNTO = "Relatório Diário de Absenteísmo"
