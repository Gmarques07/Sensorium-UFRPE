import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import logging
from typing import List, Optional
from backend.app.core.config import settings

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

def send_confirmacao_cadastro(
    email_to: str,
    nome_usuario: str,
    endereco: str
) -> bool:
    """
    Envia e-mail de confirmação de cadastro.

    Args:
        email_to: Endereço de e-mail do destinatário
        nome_usuario: Nome do usuário cadastrado
        endereco: Endereço do usuário

    Returns:
        bool: True se o e-mail foi enviado com sucesso, False caso contrário
    """
    subject = "Confirmação de Cadastro - Sensorium UFRPE"

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Confirmação de Cadastro - Sensorium UFRPE</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <tr>
            <td style="text-align: center; padding: 30px 20px; border-bottom: 2px solid #007bff;">
                <div style="font-size: 24px; font-weight: bold; color: #007bff; margin-bottom: 10px;">🌊 Sensorium UFRPE</div>
                <div style="color: #6c757d; font-size: 14px;">Sistema de Monitoramento de Qualidade da Água</div>
            </td>
        </tr>
        <tr>
            <td style="padding: 30px;">
                <h2 style="text-align: center; color: #007bff;">🎉 Cadastro Realizado com Sucesso!</h2>

                <p>Olá <strong>{nome_usuario}</strong>,</p>

                <p>Seja bem-vindo(a) ao <strong>Sensorium UFRPE</strong>! Seu cadastro foi realizado com sucesso e agora você pode acessar todas as funcionalidades do nosso sistema de monitoramento de qualidade da água.</p>

                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #007bff;">
                    <h3 style="margin-top: 0; color: #007bff; font-size: 18px;">📋 Resumo do seu Cadastro</h3>
                    <div style="margin: 10px 0; display: flex; align-items: center;">
                        <span style="font-weight: bold; min-width: 100px; color: #495057; display: inline-block;">Nome:</span>
                        <span style="color: #212529;">{nome_usuario}</span>
                    </div>
                    <div style="margin: 10px 0; display: flex; align-items: center;">
                        <span style="font-weight: bold; min-width: 100px; color: #495057; display: inline-block;">E-mail:</span>
                        <span style="color: #212529;">{email_to}</span>
                    </div>
                    <div style="margin: 10px 0; display: flex; align-items: center;">
                        <span style="font-weight: bold; min-width: 100px; color: #495057; display: inline-block;">Endereço:</span>
                        <span style="color: #212529;">{endereco}</span>
                    </div>
                    <div style="margin: 10px 0; display: flex; align-items: center;">
                        <span style="font-weight: bold; min-width: 100px; color: #495057; display: inline-block;">Status:</span>
                        <span style="color: #212529;">✅ Ativo</span>
                    </div>
                </div>

                <div style="background-color: #e7f3ff; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #007bff;">
                    <h3 style="margin-top: 0; color: #007bff; font-size: 18px;">📚 Instruções Importantes</h3>
                    <p>Para começar a usar o sistema, siga estas instruções:</p>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li style="margin: 8px 0; color: #495057;"><strong>Faça login:</strong> Acesse o sistema usando seu e-mail e senha cadastrados</li>
                        <li style="margin: 8px 0; color: #495057;"><strong>Configure sensores:</strong> Adicione e configure seus sensores de monitoramento</li>
                        <li style="margin: 8px 0; color: #495057;"><strong>Monitore dados:</strong> Visualize dados em tempo real de pH, nível da água e outros parâmetros</li>
                        <li style="margin: 8px 0; color: #495057;"><strong>Receba alertas:</strong> Configure notificações para receber alertas importantes</li>
                        <li style="margin: 8px 0; color: #495057;"><strong>Gere relatórios:</strong> Crie relatórios detalhados dos dados coletados</li>
                    </ul>
                </div>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{settings.BASE_URL}/login_usuario.html" style="display: inline-block; padding: 12px 24px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 10px 0;">
                        🚀 Acessar o Sistema
                    </a>
                </div>

                <div style="background-color: #e7f3ff; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #007bff;">
                    <h3 style="margin-top: 0; color: #007bff; font-size: 18px;">🔒 Segurança e Suporte</h3>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li style="margin: 8px 0; color: #495057;">Mantenha suas credenciais seguras e não as compartilhe</li>
                        <li style="margin: 8px 0; color: #495057;">Em caso de problemas, entre em contato conosco através do e-mail: equipesensorium@gmail.com</li>
                        <li style="margin: 8px 0; color: #495057;">Para dúvidas técnicas, consulte nossa documentação ou suporte</li>
                    </ul>
                </div>
            </td>
        </tr>
        <tr>
            <td style="text-align: center; padding: 30px 20px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; color: #6c757d; font-size: 14px;">
                <p><strong>Equipe Sensorium UFRPE</strong></p>
                <p>Universidade Federal Rural de Pernambuco</p>
                <p>📧 equipesensorium@gmail.com | 🌐 Sistema de Monitoramento de Qualidade da Água</p>
                <p style="font-size: 12px; color: #adb5bd; margin-top: 15px;">
                    Este é um e-mail automático, por favor não responda. Se precisar de ajuda, entre em contato conosco.
                </p>
            </td>
        </tr>
    </table>
</body>
</html>"""

    # Enviar e-mail
    return send_email_with_attachment(
        email_to=email_to,
        subject=subject,
        html_content=html_content
    )

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