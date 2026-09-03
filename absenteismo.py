"""
Cálculo de absenteísmo a partir de atrasos e saídas antecipadas.
"""

from datetime import datetime, date, time

import pandas as pd

import config


def _para_datetime(dia: date, horario) -> datetime:
    """Combina uma data com um horário (time, str ou timedelta) em datetime."""
    if horario is None or (isinstance(horario, float) and pd.isna(horario)):
        return None
    if isinstance(horario, str):
        horario = datetime.strptime(horario, "%H:%M:%S").time()
    if isinstance(horario, pd.Timedelta):
        horario = (datetime.min + horario).time()
    if isinstance(horario, time):
        return datetime.combine(dia, horario)
    return None


def calcular_absenteismo(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recebe o DataFrame bruto de registros (ver db.buscar_registros) e
    devolve um DataFrame linha-a-linha com as colunas adicionais:
        atraso_minutos, saida_antecipada_minutos, ocorrencia
    """
    if df.empty:
        return df.assign(
            atraso_minutos=[], saida_antecipada_minutos=[], ocorrencia=[]
        )

    registros = []
    for _, row in df.iterrows():
        dia = row["data"] if isinstance(row["data"], date) else pd.to_datetime(row["data"]).date()

        entrada_esperada = _para_datetime(dia, row["horario_entrada_esperado"])
        saida_esperada = _para_datetime(dia, row["horario_saida_esperado"])
        entrada_real = _para_datetime(dia, row["hora_entrada"])
        saida_real = _para_datetime(dia, row["hora_saida"])

        atraso_min = 0
        if entrada_real is None:
            # Sem registro de entrada -> considerar falta total do dia
            atraso_min = None
        elif entrada_esperada is not None:
            delta = (entrada_real - entrada_esperada).total_seconds() / 60
            atraso_min = max(0, round(delta))
            if atraso_min <= config.TOLERANCIA_ATRASO_MINUTOS:
                atraso_min = 0

        saida_antecip_min = 0
        if saida_real is None:
            saida_antecip_min = None
        elif saida_esperada is not None:
            delta = (saida_esperada - saida_real).total_seconds() / 60
            saida_antecip_min = max(0, round(delta))
            if saida_antecip_min <= config.TOLERANCIA_SAIDA_ANTECIPADA_MINUTOS:
                saida_antecip_min = 0

        if entrada_real is None and saida_real is None:
            ocorrencia = "Falta"
        elif atraso_min and saida_antecip_min:
            ocorrencia = "Atraso e saída antecipada"
        elif atraso_min:
            ocorrencia = "Atraso"
        elif saida_antecip_min:
            ocorrencia = "Saída antecipada"
        else:
            ocorrencia = "Regular"

        registros.append({
            **row.to_dict(),
            "atraso_minutos": atraso_min,
            "saida_antecipada_minutos": saida_antecip_min,
            "ocorrencia": ocorrencia,
        })

    return pd.DataFrame(registros)


def resumir_por_funcionario(df_calculado: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega os dados diários em um resumo por funcionário:
        nome, email, dias_com_ocorrencia, total_atraso_min, total_saida_antecipada_min
    """
    if df_calculado.empty:
        return pd.DataFrame(columns=[
            "nome", "dias_com_ocorrencia",
            "total_atraso_min", "total_saida_antecipada_min"
        ])

    df = df_calculado.copy()
    df["tem_ocorrencia"] = df["ocorrencia"] != "Regular"

    resumo = df.groupby(["nome"]).agg(
        dias_com_ocorrencia=("tem_ocorrencia", "sum"),
        total_atraso_min=("atraso_minutos", lambda s: s.fillna(0).sum()),
        total_saida_antecipada_min=("saida_antecipada_minutos", lambda s: s.fillna(0).sum()),
    ).reset_index()

    return resumo.sort_values("dias_com_ocorrencia", ascending=False)
