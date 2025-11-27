from datetime import datetime
from zoneinfo import ZoneInfo
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

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alerta de Sensor Violado - Sensorium UFRPE</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <tr>
            <td style="text-align: center; padding: 30px 20px; border-bottom: 2px solid #dc3545;">
                <div style="font-size: 24px; font-weight: bold; color: #dc3545; margin-bottom: 10px;">🚨 Sensorium UFRPE</div>
                <div style="color: #6c757d; font-size: 14px;">Sistema de Monitoramento de Qualidade da Água</div>
            </td>
        </tr>
        <tr>
            <td style="padding: 30px;">
                <h2 style="text-align: center; color: #dc3545;">⚠️ Alerta de Sensor Acionado!</h2>

                <p>Olá <strong>{nome_usuario}</strong>,</p>

                <p>Um alerta foi acionado no <strong>Sensorium UFRPE</strong>! Detectamos uma violação de regra configurada em um dos seus sensores de monitoramento de qualidade da água.</p>

                <div style="background-color: #f8d7da; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #dc3545;">
                    <h3 style="margin-top: 0; color: #721c24; font-size: 18px;">🚨 Detalhes do Alerta</h3>
                    <p>{mensagem_usar}</p>
                </div>

                <div style="background-color: #e2e3e5; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #6c757d;">
                    <h3 style="margin-top: 0; color: #383d41; font-size: 18px;">📊 Informações do Sensor</h3>
                    <div style="margin: 10px 0; display: flex; align-items: center;">
                        <span style="font-weight: bold; min-width: 120px; color: #495057; display: inline-block;">Sensor:</span>
                        <span style="color: #212529;">{nome_sensor}</span>
                    </div>
                    <div style="margin: 10px 0; display: flex; align-items: center;">
                        <span style="font-weight: bold; min-width: 120px; color: #495057; display: inline-block;">Regra Configurada:</span>
                        <span style="color: #212529;">{descricao_regra}</span>
                    </div>
                    <div style="margin: 10px 0; display: flex; align-items: center;">
                        <span style="font-weight: bold; min-width: 120px; color: #495057; display: inline-block;">Valor Atual:</span>
                        <span style="color: #212529;">{valor_atual}</span>
                    </div>
                    <div style="margin: 10px 0; display: flex; align-items: center;">
                        <span style="font-weight: bold; min-width: 120px; color: #495057; display: inline-block;">Data/Hora:</span>
                        <span style="color: #212529;">{datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%d/%m/%Y %H:%M:%S")}</span>
                    </div>
                </div>

                <div style="background-color: #d1ecf1; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #17a2b8;">
                    <h3 style="margin-top: 0; color: #0c5460; font-size: 18px;">🔧 Recomendações</h3>
                    <p>Para resolver esta situação, sugerimos as seguintes ações:</p>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li style="margin: 8px 0; color: #495057;"><strong>Verifique os dados:</strong> Acesse o painel para visualizar os dados em tempo real</li>
                        <li style="margin: 8px 0; color: #495057;"><strong>Analise os dados:</strong> Confira as leituras recentes do sensor para entender o problema</li>
                        <li style="margin: 8px 0; color: #495057;"><strong>Tome ação:</strong> Realize as correções necessárias no seu sistema</li>
                        <li style="margin: 8px 0; color: #495057;"><strong>Atualize regras:</strong> Se necessário, ajuste as regras de alerta no painel</li>
                    </ul>
                </div>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{settings.BASE_URL}" style="display: inline-block; padding: 12px 24px; background-color: #dc3545; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 10px 0;">
                        📊 Acessar Painel de Alertas
                    </a>
                </div>

                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #6c757d;">
                    <h3 style="margin-top: 0; color: #495057; font-size: 18px;">ℹ️ Informações Adicionais</h3>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li style="margin: 8px 0; color: #495057;">Mantenha-se atento a outros alertas que possam surgir</li>
                        <li style="margin: 8px 0; color: #495057;">Em caso de dúvidas, entre em contato conosco através do e-mail: equipesensorium@gmail.com</li>
                        <li style="margin: 8px 0; color: #495057;">Consulte nossa documentação para mais informações sobre regras de alerta</li>
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