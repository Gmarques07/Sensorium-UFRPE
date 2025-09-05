#!/usr/bin/env python3
"""
Script para testar o envio de e-mails.
"""

import sys
import os

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.email import send_email_with_attachment

def testar_envio_email():
    """Testa o envio de um e-mail simples."""
    print("Testando envio de e-mail...")
    
    # Dados de teste
    email_to = "teste@exemplo.com"
    subject = "Teste de Envio de E-mail"
    html_content = """
    <html>
      <body>
        <h2>Teste de Envio de E-mail</h2>
        <p>Este é um e-mail de teste para verificar se o sistema de envio está funcionando corretamente.</p>
        <p>Se você recebeu este e-mail, significa que as configurações de e-mail estão corretas.</p>
        <p>Atenciosamente,<br>Equipe Sensorium UFRPE</p>
      </body>
    </html>
    """
    
    # Enviar e-mail
    sucesso = send_email_with_attachment(
        email_to=email_to,
        subject=subject,
        html_content=html_content
    )
    
    if sucesso:
        print("E-mail enviado com sucesso!")
        return True
    else:
        print("Falha ao enviar e-mail.")
        return False

if __name__ == "__main__":
    testar_envio_email()