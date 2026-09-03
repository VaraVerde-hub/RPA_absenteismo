"""
Envio do relatório de absenteísmo por email (HTML com tabela).
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd

import config


def _montar_html(resumo: pd.DataFrame, detalhado: pd.DataFrame) -> str:
    if resumo.empty:
        corpo_tabela = "<p>Nenhum registro encontrado no período.</p>"
    else:
        corpo_tabela = resumo.to_html(index=False, justify="left")

    return f"""
    <html>
      <body>
        <h2>Relatório Diário de Absenteísmo</h2>
        <p>Resumo por funcionário (atrasos e saídas antecipadas):</p>
        {corpo_tabela}
        <br>
        <p style="font-size: 12px; color: #666;">
            Relatório gerado automaticamente. Este email contém dados
            confidenciais de RH — não encaminhar sem autorização.
        </p>
      </body>
    </html>
    """


def enviar_relatorio(resumo: pd.DataFrame, detalhado: pd.DataFrame):
    if not config.SMTP_USER or not config.SMTP_PASSWORD:
        raise RuntimeError(
            "SMTP_USER / SMTP_PASSWORD não configurados. Defina as "
            "variáveis de ambiente antes de rodar a automação."
        )
    if not config.EMAIL_DESTINATARIOS:
        raise RuntimeError(
            "EMAIL_DESTINATARIOS não configurado. Defina a variável de "
            "ambiente com os emails separados por vírgula."
        )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = config.EMAIL_ASSUNTO
    msg["From"] = config.SMTP_USER
    msg["To"] = ", ".join(config.EMAIL_DESTINATARIOS)

    html = _montar_html(resumo, detalhado)
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as servidor:
        servidor.starttls()
        servidor.login(config.SMTP_USER, config.SMTP_PASSWORD)
        servidor.sendmail(config.SMTP_USER, config.EMAIL_DESTINATARIOS, msg.as_string())

    print(f"Email enviado com sucesso para: {', '.join(config.EMAIL_DESTINATARIOS)}")
