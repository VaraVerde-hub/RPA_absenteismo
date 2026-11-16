from datetime import date
import pandas as pd
from absenteismo import calcular_absenteismo, resumir_por_funcionario

def linha(**kw):
    row = dict(funcionario_id=1, nome="Pessoa", data=date(2026, 11, 13),
               horario_entrada_esperado="08:00:00",
               horario_saida_esperado="17:00:00",
               hora_entrada="08:00:00", hora_saida="17:00:00")
    row.update(kw)
    return row

def status(**kw):
    return calcular_absenteismo(pd.DataFrame([linha(**kw)])).iloc[0]

def test_regular():
    assert status()["ocorrencia"] == "Regular"

def test_tolerancia_exata():
    assert status(hora_entrada="08:10:00")["ocorrencia"] == "Regular"

def test_atraso():
    assert status(hora_entrada="08:25:00")["atraso_minutos"] == 25

def test_saida_antecipada():
    assert status(hora_saida="16:30:00")["ocorrencia"] == "Saída antecipada"

def test_falta():
    assert status(hora_entrada=None, hora_saida=None)["ocorrencia"].startswith("Falta")

def test_registro_incompleto():
    assert status(hora_entrada=None)["ocorrencia"] == "Registro incompleto"

def test_turno_noturno():
    item = status(horario_entrada_esperado="22:00:00",
                  horario_saida_esperado="06:00:00",
                  hora_entrada="22:15:00", hora_saida="05:45:00")
    assert item["atraso_minutos"] == 15
    assert item["saida_antecipada_minutos"] == 15

def test_homonimos_nao_agrupados():
    dados = pd.DataFrame([linha(), linha(funcionario_id=2, hora_entrada="08:30:00")])
    resumo = resumir_por_funcionario(calcular_absenteismo(dados))
    assert len(resumo) == 2

def test_dataframe_vazio():
    df = pd.DataFrame(columns=list(linha().keys()))
    assert calcular_absenteismo(df).empty

def test_jornada_ausente():
    assert status(horario_entrada_esperado=None)["ocorrencia"] == "Escala não configurada"
