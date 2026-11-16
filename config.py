"""Centralized, environment-only configuration. No credentials in source."""
import os
from dataclasses import dataclass
from sqlalchemy.engine import URL

TOLERANCIA_ATRASO_MINUTOS = int(os.getenv("TOLERANCIA_ATRASO_MINUTOS", "10"))
TOLERANCIA_SAIDA_ANTECIPADA_MINUTOS = int(os.getenv("TOLERANCIA_SAIDA_ANTECIPADA_MINUTOS", "10"))
PERIODO_RELATORIO_DIAS = int(os.getenv("PERIODO_RELATORIO_DIAS", "1"))
# Comma-separated ISO dates; use an authoritative holiday calendar in production.
FERIADOS = set(filter(None, (x.strip() for x in os.getenv("FERIADOS", "").split(","))))
DIAS_TRABALHO = {int(x) for x in os.getenv("DIAS_TRABALHO", "0,1,2,3,4").split(",") if x.strip()}
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_DESTINATARIOS = [x.strip() for x in os.getenv("EMAIL_DESTINATARIOS", "").split(",") if x.strip()]
EMAIL_ASSUNTO = os.getenv("EMAIL_ASSUNTO", "Relatório Diário de Absenteísmo")

# Column and table names must be administrator-supplied constants, not user input.
TABELA_FUNCIONARIOS = "[db_catraca].[dbo].[Funcionarios]"
COL_FUNC_ID = "[IdFuncionario]"
COL_FUNC_NOME = "[Nome]"
COL_FUNC_HORARIO_ENTRADA_ESPERADO = "[JornadaInicio]"
COL_FUNC_HORARIO_SAIDA_ESPERADO = "[JornadaFim]"
TABELA_REGISTROS = "[db_catraca].[dbo].[registros_ponto]"
COL_REG_ID = "[funcionario_id]"
COL_REG_DATA = "[data]"
COL_REG_HORA_ENTRADA = "[hora_entrada]"
COL_REG_HORA_SAIDA = "[hora_saida]"

def database_url():
    """Use DB_CONNECTION_STRING or safe SQLAlchemy URL assembly."""
    supplied = os.getenv("DB_CONNECTION_STRING")
    if supplied:
        return supplied
    required = ("DB_SERVER", "DB_NAME", "DB_USER", "DB_PASSWORD")
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise RuntimeError("Database configuration missing: " + ", ".join(missing))
    return URL.create(
        "mssql+pyodbc",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_SERVER"],
        database=os.environ["DB_NAME"],
        query={"driver": os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server"),
               "Encrypt": "yes", "TrustServerCertificate": "no"},
    )
