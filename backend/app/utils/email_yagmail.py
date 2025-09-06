import yagmail
import logging
from typing import Optional
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

def send_email_with_yagmail(
    email_to: str,
    subject: str,
    html_content: str,
    attachment_data: Optional[bytes] = None,
    attachment_filename: Optional[str] = None
) -> bool:
    """
    Envia um e-mail com anexo (opcional) usando yagmail.
    
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
        # Criar conexão com yagmail
        yag = yagmail.SMTP(
            user=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            host=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            smtp_ssl=False,  # Usar STARTTLS
            smtp_starttls=True
        )
        
        # Preparar anexos, se houver
        attachments = []
        if attachment_data and attachment_filename:
            # Salvar temporariamente o arquivo
            with open(attachment_filename, 'wb') as f:
                f.write(attachment_data)
            attachments.append(attachment_filename)
        
        # Enviar e-mail
        yag.send(
            to=email_to,
            subject=subject,
            contents=[html_content],
            attachments=attachments
        )
        
        # Limpar arquivo temporário, se criado
        if attachment_data and attachment_filename:
            import os
            if os.path.exists(attachment_filename):
                os.remove(attachment_filename)
        
        logger.info(f"E-mail enviado com sucesso para {email_to}")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail para {email_to}: {str(e)}")
        # Limpar arquivo temporário em caso de erro
        if attachment_data and attachment_filename:
            import os
            if os.path.exists(attachment_filename):
                os.remove(attachment_filename)
        return False

def send_relatorio_por_email_yagmail(
    email_to: str,
    pdf_data: bytes,
    inicio: str,
    fim: str,
    dispositivo: Optional[str] = None
) -> bool:
    """
    Envia o relatório PDF por e-mail usando yagmail.
    
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
    return send_email_with_yagmail(
        email_to=email_to,
        subject=subject,
        html_content=html_content,
        attachment_data=pdf_data,
        attachment_filename=filename
    )