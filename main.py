"""
Script principal: busca os registros, calcula o absenteísmo e envia o
email com o relatório.

Uso:
    python main.py

Para rodar automaticamente todo dia, agende este script no cron
(Linux/Mac) ou no Agendador de Tarefas (Windows). Veja o README.md.
"""

from dotenv import load_dotenv
load_dotenv()

import sys
import traceback
from datetime import datetime

import db
import absenteismo
import email_sender


def main():
    print(f"[{datetime.now()}] Iniciando geração do relatório de absenteísmo...")

    try:
        df_bruto = db.buscar_registros()
        print(f"  -> {len(df_bruto)} registros encontrados no período.")

        df_calculado = absenteismo.calcular_absenteismo(df_bruto)
        resumo = absenteismo.resumir_por_funcionario(df_calculado)

        email_sender.enviar_relatorio(resumo, df_calculado)

        print(f"[{datetime.now()}] Concluído com sucesso.")

    except Exception as e:
        print(f"[{datetime.now()}] ERRO: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
