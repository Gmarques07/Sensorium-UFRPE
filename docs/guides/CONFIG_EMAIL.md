# Configuração de Envio de E-mails

Para habilitar o envio de e-mails (confirmações de cadastro e relatórios), você precisa configurar as variáveis de ambiente no arquivo `.env`:

## Configuração para Gmail (Recomendado)

Para usar o e-mail oficial do Sensorium (equipesensorium@gmail.com), adicione as seguintes linhas ao seu arquivo `.env`:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=equipesensorium@gmail.com
SMTP_PASSWORD=hbpl kcxg ndho zwra
EMAILS_FROM_EMAIL=equipesensorium@gmail.com
EMAILS_FROM_NAME=Sensorium UFRPE
```

**Importante:** Para o Gmail, você precisa usar uma "senha de app" em vez da sua senha normal:
1. Habilite a autenticação de dois fatores na sua conta do Gmail
2. Acesse as configurações de segurança do Google
3. Gere uma senha de app para o Sensorium
4. Use essa senha de app no campo `SMTP_PASSWORD`

## Configuração para seu próprio Gmail

Se você quiser usar seu próprio Gmail, adicione as seguintes linhas ao seu arquivo `.env`:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_de_app
EMAILS_FROM_EMAIL=seu_email@gmail.com
EMAILS_FROM_NAME=Sensorium UFRPE
```

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

## Funcionalidades de E-mail

O sistema agora envia automaticamente:

### 📧 E-mail de Confirmação de Cadastro
- Enviado automaticamente quando um usuário se cadastra
- Contém informações do cadastro (nome, e-mail, endereço)
- Inclui instruções importantes para usar o sistema
- Template HTML responsivo e profissional

### 📊 E-mail de Relatórios
- Enviado quando o usuário solicita relatórios
- Contém o arquivo PDF em anexo
- Inclui informações sobre o período e dispositivo

## Testando a configuração

### Teste Automático
Execute o script de teste para verificar se o e-mail está funcionando:

```bash
cd backend
python scripts/teste_email_cadastro.py
```

### Teste Manual
1. Configure as variáveis de ambiente no arquivo `.env`
2. Reinicie o servidor
3. Faça um novo cadastro de usuário
4. Verifique se o e-mail de confirmação foi recebido

## Troubleshooting

### E-mails não são enviados
- Verifique se todas as variáveis de ambiente estão configuradas
- Confirme se a senha de app do Gmail está correta
- Verifique os logs do servidor para erros específicos

### E-mail vai para spam
- Adicione o e-mail remetente à sua lista de contatos
- Verifique se o provedor de e-mail não está bloqueando o envio

### Erro de autenticação
- Para Gmail, certifique-se de usar uma senha de app, não a senha normal
- Verifique se a autenticação de dois fatores está habilitada