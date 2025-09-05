import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import logging
from typing import List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

def send_email_with_attachment(
    email_to: str,
    subject: str,
    html_content: str,
    attachment_data: Optional[bytes] = None,
    attachment_filename: Optional[str] = None
) -> bool:
    """
    Envia um e-mail com anexo (opcional).
    
    Args:
        email_to: Endereço de e-mail do destinatário
        subject: Assunto do e-mail
        html_content: Conteúdo HTML do e-mail
        attachment_data: Dados do arquivo em bytes (opcional)
        attachment_filename: Nome do arquivo anexado (opcional)
        
    Returns:
        bool: True se o e-mail foi enviado com sucesso, False caso contrário
    """
    if not settings.emails_enabled:
        logger.warning("E-mails não estão configurados. Pulando envio.")
        return False
    
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
        message["To"] = email_to
        
        # Parte HTML
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        
        # Anexo, se fornecido
        if attachment_data and attachment_filename:
            part = MIMEBase('application', "octet-stream")
            part.set_payload(attachment_data)
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {attachment_filename}',
            )
            message.attach(part)
        
        # Criar conexão segura com o servidor
        context = ssl.create_default_context()
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAILS_FROM_EMAIL, email_to, message.as_string())
        
        logger.info(f"E-mail enviado com sucesso para {email_to}")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail para {email_to}: {str(e)}")
        return False

def send_relatorio_por_email(
    email_to: str,
    pdf_data: bytes,
    inicio: str,
    fim: str,
    dispositivo: Optional[str] = None
) -> bool:
    """
    Envia o relatório PDF por e-mail.
    
    Args:
        email_to: Endereço de e-mail do destinatário
        pdf_data: Dados do PDF em bytes
        inicio: Data inicial do relatório
        fim: Data final do relatório
        dispositivo: Nome do dispositivo (opcional)
        
    Returns:
        bool: True se o e-mail foi enviado com sucesso, False caso contrário
    """
    # Criar conteúdo HTML do e-mail
    dispositivo_texto = f" - {dispositivo}" if dispositivo else ""
    subject = f"Relatório Sensorium{dispositivo_texto} ({inicio} a {fim})"
    
    html_content = f"""
    <html>
      <body>
        <h2>Relatório de Monitoramento - Sensorium UFRPE</h2>
        <p>Olá,</p>
        <p>Seu relatório de monitoramento está em anexo.</p>
        <p><strong>Período:</strong> {inicio} a {fim}</p>
        {f"<p><strong>Dispositivo:</strong> {dispositivo}</p>" if dispositivo else ""}
        <p>Atenciosamente,<br>Equipe Sensorium UFRPE</p>
      </body>
    </html>
    """
    
    # Nome do arquivo
    dispositivo_nome = f"_{dispositivo}" if dispositivo else ""
    filename = f"relatorio{dispositivo_nome}_{inicio.replace('/', '')}_{fim.replace('/', '')}.pdf"
    
    # Enviar e-mail
    return send_email_with_attachment(
        email_to=email_to,
        subject=subject,
        html_content=html_content,
        attachment_data=pdf_data,
        attachment_filename=filename
    )