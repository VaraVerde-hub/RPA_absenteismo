"""SMTP mail delivery; disabled unless explicitly requested by main."""
import smtplib
import ssl
from email.message import EmailMessage
import config

def montar_html(resumo):
    body = "<p>Nenhum registro no período.</p>" if resumo.empty else resumo.to_html(index=False, escape=True)
    return "<h2>Relatório de absenteísmo</h2>" + body + "<p>Confidencial — uso autorizado de RH.</p>"

def enviar_relatorio(resumo, detalhado=None):
    if not all([config.SMTP_HOST, config.SMTP_USER, config.SMTP_PASSWORD, config.EMAIL_DESTINATARIOS]):
        raise RuntimeError("SMTP settings incomplete; refusing to send")
    msg = EmailMessage()
    msg["Subject"] = config.EMAIL_ASSUNTO
    msg["From"] = config.SMTP_USER
    msg["To"] = ", ".join(config.EMAIL_DESTINATARIOS)
    msg.set_content("Relatório de absenteísmo. Visualize a versão HTML.")
    msg.add_alternative(montar_html(resumo), subtype="html")
    # STARTTLS requires a verified TLS handshake before authentication.
    with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=20) as server:
        server.ehlo()
        server.starttls(context=ssl.create_default_context())
        server.ehlo()
        server.login(config.SMTP_USER, config.SMTP_PASSWORD)
        server.send_message(msg)
