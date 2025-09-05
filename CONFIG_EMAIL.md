# Configuração de Envio de E-mails

Para habilitar o envio de relatórios por e-mail, você precisa configurar as variáveis de ambiente no arquivo `.env`:

## Configuração para Gmail

Se você estiver usando Gmail, adicione as seguintes linhas ao seu arquivo `.env`:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_de_app
EMAILS_FROM_EMAIL=seu_email@gmail.com
EMAILS_FROM_NAME=Sensorium UFRPE
```

**Importante:** Para o G

mail, você precisa usar uma "senha de app" em vez da sua senha normal:
1. Habilite a autenticação de dois fatores na sua conta do Gmail
2. Acesse as configurações de segurança do Google
3. Gere uma senha de app para o Sensorium
4. Use essa senha de app no campo `SMTP_PASSWORD`

## Configuração para Outlook/Hotmail

```
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=seu_email@outlook.com
SMTP_PASSWORD=sua_senha
EMAILS_FROM_EMAIL=seu_email@outlook.com
EMAILS_FROM_NAME=Sensorium UFRPE
```

## Configuração para outros provedores SMTP

Para outros provedores, consulte a documentação do seu provedor de e-mail para obter os valores corretos de:
- SMTP_HOST
- SMTP_PORT
- SMTP_USER
- SMTP_PASSWORD
- EMAILS_FROM_EMAIL

## Testando a configuração

Após configurar, reinicie o servidor e tente enviar um relatório por e-mail.