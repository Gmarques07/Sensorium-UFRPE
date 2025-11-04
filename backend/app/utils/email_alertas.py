from datetime import datetime
import logging
from backend.app.core.config import settings
from backend.app.utils.email_yagmail import send_email_with_yagmail

logger = logging.getLogger(__name__)

def send_alerta_violacao_regra(
    email_to: str,
    nome_usuario: str,
    nome_sensor: str,
    descricao_regra: str,
    valor_atual: float,
    mensagem_alerta: str
) -> bool:
    """
    Envia e-mail de alerta quando uma regra de alerta é violada.
    
    Args:
        email_to: Endereço de e-mail do destinatário
        nome_usuario: Nome do usuário proprietário da regra
        nome_sensor: Nome do sensor que acionou o alerta
        descricao_regra: Descrição da regra violada (ex: "pH > 7.0")
        valor_atual: Valor atual que violou a regra
        mensagem_alerta: Mensagem personalizada do alerta
        
    Returns:
        bool: True se o e-mail foi enviado com sucesso, False caso contrário
    """
    subject = f"🚨 Alerta de Sensor Violado - {nome_sensor}"
    
    mensagem_padrao = f"A regra configurada '{descricao_regra}' foi violada no sensor '{nome_sensor}'."
    mensagem_usar = mensagem_alerta if mensagem_alerta else mensagem_padrao
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Alerta de Sensor Violado - Sensorium UFRPE</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f8f9fa;
            }}
            .container {{
                background-color: #ffffff;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 2px solid #dc3545;
            }}
            .header h1 {{
                color: #dc3545;
                margin: 0;
                font-size: 28px;
            }}
            .alert-info {{
                background-color: #f8d7da;
                border: 1px solid #f5c6cb;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
            }}
            .alert-info h2 {{
                color: #721c24;
                margin-top: 0;
            }}
            .sensor-details {{
                background-color: #e2e3e5;
                border: 1px solid #d6d8db;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
            }}
            .sensor-details h3 {{
                color: #383d41;
                margin-top: 0;
            }}
            .info-item {{
                margin: 10px 0;
                padding: 10px;
                background-color: white;
                border-radius: 5px;
            }}
            .timestamp {{
                font-size: 0.9em;
                color: #6c757d;
                text-align: right;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚨 Alerta de Sensor</h1>
                <p><strong>Sistema Sensorium UFRPE</strong></p>
            </div>
            
            <div class="alert-info">
                <h2>Regra de Alerta Violada!</h2>
                <p>Olá <strong>{nome_usuario}</strong>,</p>
                <p>{mensagem_usar}</p>
            </div>
            
            <div class="sensor-details">
                <h3>Detalhes do Alerta</h3>
                
                <div class="info-item">
                    <strong>_sensor:</strong> {nome_sensor}
                </div>
                
                <div class="info-item">
                    <strong>Regra Configurada:</strong> {descricao_regra}
                </div>
                
                <div class="info-item">
                    <strong>Valor Atual:</strong> {valor_atual}
                </div>
                
                <div class="info-item">
                    <strong>Data/Hora:</strong> {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
                </div>
            </div>
            
            <p>Por favor, acesse o painel do Sensorium para mais detalhes e ações necessárias.</p>
            
            <div class="timestamp">
                Enviado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        if not settings.emails_enabled:
            logger.warning("Envio de e-mails desabilitado nas configurações")
            return False
            
        sucesso = send_email_with_yagmail(
            email_to=email_to,
            subject=subject,
            html_content=html_content
        )
        
        if sucesso:
            logger.info(f"E-mail de alerta enviado com sucesso para {email_to}")
        else:
            logger.warning(f"Falha ao enviar e-mail de alerta para {email_to}")
            
        return sucesso
        
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail de alerta para {email_to}: {str(e)}")
        return False