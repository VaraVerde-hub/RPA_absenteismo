"""
validar

Camada de acesso ao banco de dados.

Usa SQLAlchemy, então funciona com PostgreSQL, MySQL, SQL Server, SQLite
etc., bastando trocar a DB_CONNECTION_STRING no config.py.
"""

from datetime import date, timedelta

import pandas as pd
from sqlalchemy import create_engine, text

import config


def get_engine():
    if not config.connection_string:
        raise RuntimeError(
            "DB_CONNECTION_STRING não configurada. Defina a variável de "
            "ambiente ou edite config.py."
        )
    return create_engine(config.connection_string)


def buscar_registros(dias: int = None) -> pd.DataFrame:
    """
    Busca os registros de ponto dos funcionários dos últimos `dias` dias,
    já unindo com os dados cadastrais de cada funcionário.

    Retorna um DataFrame com colunas:
        funcionario_id, nome, email,
        horario_entrada_esperado, horario_saida_esperado,
        data, hora_entrada, hora_saida
    """
    dias = dias or config.PERIODO_RELATORIO_DIAS
    data_inicio = date.today() - timedelta(days=dias)

    query = text(f"""
        SELECT
            f.{config.COL_FUNC_ID}          AS funcionario_id,
            f.{config.COL_FUNC_NOME}        AS nome,
            f.{config.COL_FUNC_HORARIO_ENTRADA_ESPERADO} AS horario_entrada_esperado,
            f.{config.COL_FUNC_HORARIO_SAIDA_ESPERADO}   AS horario_saida_esperado,
            r.{config.COL_REG_DATA}         AS data,
            r.{config.COL_REG_HORA_ENTRADA} AS hora_entrada,
            r.{config.COL_REG_HORA_SAIDA}   AS hora_saida
        FROM {config.TABELA_REGISTROS} r
        JOIN {config.TABELA_FUNCIONARIOS} f
            ON r.{config.COL_REG_ID} = f.{config.COL_FUNC_ID}
        WHERE r.{config.COL_REG_DATA} >= :data_inicio
        ORDER BY f.{config.COL_FUNC_NOME}, r.{config.COL_REG_DATA}
    """)

    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"data_inicio": data_inicio})

    #print(df)
    return df

#buscar_registros(7)
