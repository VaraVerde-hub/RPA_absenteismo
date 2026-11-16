"""Database access. Queries are read-only and date-bound."""
from datetime import date, timedelta
import pandas as pd
from sqlalchemy import create_engine, text
import config

def get_engine():
    return create_engine(config.database_url(), pool_pre_ping=True, connect_args={"timeout": 15})

def buscar_registros(dias=None, hoje=None, engine=None):
    """Build expected working dates, including employees without any time record.

    Assumes weekday schedules for every employee. Configure a real shift calendar
    before using results for employment decisions.
    """
    dias = config.PERIODO_RELATORIO_DIAS if dias is None else dias
    if dias <= 0:
        raise ValueError("dias must be positive")
    hoje = hoje or date.today()
    inicio = hoje - timedelta(days=dias)
    datas = [inicio + timedelta(days=i) for i in range(dias)]
    datas = [d for d in datas if d.weekday() in config.DIAS_TRABALHO and d.isoformat() not in config.FERIADOS]
    query_func = text(f"""
        SELECT {config.COL_FUNC_ID} AS funcionario_id,
               {config.COL_FUNC_NOME} AS nome,
               {config.COL_FUNC_HORARIO_ENTRADA_ESPERADO} AS horario_entrada_esperado,
               {config.COL_FUNC_HORARIO_SAIDA_ESPERADO} AS horario_saida_esperado
        FROM {config.TABELA_FUNCIONARIOS}
    """)
    query_ponto = text(f"""
        SELECT {config.COL_REG_ID} AS funcionario_id,
               {config.COL_REG_DATA} AS data,
               {config.COL_REG_HORA_ENTRADA} AS hora_entrada,
               {config.COL_REG_HORA_SAIDA} AS hora_saida
        FROM {config.TABELA_REGISTROS}
        WHERE {config.COL_REG_DATA} >= :inicio AND {config.COL_REG_DATA} < :fim
    """)
    owned = engine is None
    engine = engine or get_engine()
    try:
        with engine.connect() as conn:
            funcionarios = pd.read_sql(query_func, conn)
            pontos = pd.read_sql(query_ponto, conn, params={"inicio": inicio, "fim": hoje})
    finally:
        if owned:
            engine.dispose()
    cols = ["funcionario_id", "nome", "horario_entrada_esperado", "horario_saida_esperado",
            "data", "hora_entrada", "hora_saida"]
    if funcionarios.empty or not datas:
        return pd.DataFrame(columns=cols)
    # Dates expected by policy, rather than only those with a recorded punch.
    calendario = pd.DataFrame({"data": datas})
    funcionarios["_join"] = 1
    calendario["_join"] = 1
    esperado = funcionarios.merge(calendario, on="_join").drop(columns="_join")
    if not pontos.empty:
        pontos["data"] = pd.to_datetime(pontos["data"]).dt.date
        # Multiple rows for one employee/day are ambiguous. Do not silently double-count.
        if pontos.duplicated(["funcionario_id", "data"]).any():
            raise ValueError("Multiple attendance rows for one employee/day; normalize punch records first")
    return esperado.merge(pontos, how="left", on=["funcionario_id", "data"])[cols]
