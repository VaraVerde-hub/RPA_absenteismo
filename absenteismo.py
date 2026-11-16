"""Pure, testable absenteeism classification for daily attendance rows."""
from datetime import date, datetime, time, timedelta
import pandas as pd
import config

def _horario(value):
    if value is None or pd.isna(value):
        return None
    if isinstance(value, datetime):
        return value.time()
    if isinstance(value, time):
        return value
    if isinstance(value, (timedelta, pd.Timedelta)):
        seconds = int(value.total_seconds())
        if not 0 <= seconds < 86400:
            raise ValueError("Time offset outside a single day")
        return (datetime.min + timedelta(seconds=seconds)).time()
    if isinstance(value, str):
        return time.fromisoformat(value.strip())
    raise ValueError("Unsupported time value")

def _momento(dia, horario, seguinte=False):
    return datetime.combine(dia + timedelta(days=int(seguinte)), horario) if horario else None

def calcular_absenteismo(df, tolerancia_atraso=None, tolerancia_saida=None):
    tolerancia_atraso = config.TOLERANCIA_ATRASO_MINUTOS if tolerancia_atraso is None else tolerancia_atraso
    tolerancia_saida = config.TOLERANCIA_SAIDA_ANTECIPADA_MINUTOS if tolerancia_saida is None else tolerancia_saida
    if min(tolerancia_atraso, tolerancia_saida) < 0:
        raise ValueError("Tolerances cannot be negative")
    out = []
    for _, row in df.iterrows():
        item = row.to_dict()
        dia = pd.to_datetime(item["data"]).date()
        expected_in = _horario(item["horario_entrada_esperado"])
        expected_out = _horario(item["horario_saida_esperado"])
        actual_in = _horario(item["hora_entrada"])
        actual_out = _horario(item["hora_saida"])
        if expected_in is None or expected_out is None:
            status, late, early = "Escala não configurada", None, None
        elif actual_in is None and actual_out is None:
            status, late, early = "Falta (não justificada no cadastro)", None, None
        elif actual_in is None or actual_out is None:
            status, late, early = "Registro incompleto", None, None
        else:
            overnight = expected_out <= expected_in
            start = _momento(dia, expected_in)
            end = _momento(dia, expected_out, overnight)
            entered = _momento(dia, actual_in)
            # An arrival in the early hours may belong to an overnight shift.
            if overnight and actual_in < expected_out:
                entered += timedelta(days=1)
            exited = _momento(dia, actual_out, actual_out <= actual_in)
            # If a night shift starts and ends at unusual clock hours, surface ambiguity.
            if overnight and exited < entered:
                exited += timedelta(days=1)
            late = max(0, round((entered - start).total_seconds() / 60))
            early = max(0, round((end - exited).total_seconds() / 60))
            late = late if late > tolerancia_atraso else 0
            early = early if early > tolerancia_saida else 0
            if late and early:
                status = "Atraso e saída antecipada"
            elif late:
                status = "Atraso"
            elif early:
                status = "Saída antecipada"
            else:
                status = "Regular"
        item.update(atraso_minutos=late, saida_antecipada_minutos=early, ocorrencia=status)
        out.append(item)
    return pd.DataFrame(out, columns=list(df.columns) + ["atraso_minutos", "saida_antecipada_minutos", "ocorrencia"])

def resumir_por_funcionario(df):
    cols = ["funcionario_id", "nome", "dias_com_ocorrencia", "total_atraso_min", "total_saida_antecipada_min"]
    if df.empty:
        return pd.DataFrame(columns=cols)
    work = df.copy()
    work["tem_ocorrencia"] = work["ocorrencia"].ne("Regular")
    result = work.groupby(["funcionario_id", "nome"], dropna=False).agg(
        dias_com_ocorrencia=("tem_ocorrencia", "sum"),
        total_atraso_min=("atraso_minutos", "sum"),
        total_saida_antecipada_min=("saida_antecipada_minutos", "sum"),
    ).reset_index()
    return result[cols].sort_values("dias_com_ocorrencia", ascending=False)
