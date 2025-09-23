# Configuração do Sistema de E-mail de Confirmação de Cadastro

## 📧 Visão Geral

O sistema Sensorium UFRPE agora envia automaticamente e-mails de confirmação quando um usuário se cadastra. O e-mail contém:

- ✅ Confirmação de que o cadastro foi realizado com sucesso
- 📋 Resumo dos dados cadastrados (nome, e-mail, endereço)
- 📚 Instruções importantes para usar o sistema
- 🔗 Link direto para acessar o sistema
- 🔒 Informações de segurança e suporte

## ⚙️ Configuração

### 1. Criar arquivo .env

Crie um arquivo `.env` na raiz do projeto (ou no diretório `backend/`) com as seguintes configurações:

```env
# Configurações do banco de dados
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=sensorium_db

# Configuração JWT
SECRET_KEY=sua_chave_secreta_aqui_deve_ser_bem_longa_e_segura
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# URL base
BASE_URL=http://localhost:8000

# Ambiente
ENVIRONMENT=development

# Configurações de e-mail para Sensorium (Obrigatório)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=equipesensorium@gmail.com
SMTP_PASSWORD=hbpl kcxg ndho zwra
EMAILS_FROM_EMAIL=equipesensorium@gmail.com
EMAILS_FROM_NAME=Sensorium UFRPE
```

### 2. Instalar dependências

```bash
cd backend
pip install -r config/requirements.txt
```

### 3. Testar a configuração

Execute o script de teste para verificar se o e-mail está funcionando:

```bash
cd backend
python scripts/teste_email_cadastro.py
```

## 🚀 Como Funciona

### Fluxo Automático

1. **Usuário se cadastra** através do formulário de cadastro
2. **Sistema cria a conta** no banco de dados
3. **E-mail é enviado automaticamente** com confirmação
4. **Token de acesso é retornado** para login imediato

### Conteúdo do E-mail

O e-mail de confirmação inclui:

- **Cabeçalho profissional** com logo do Sensorium
- **Mensagem de boas-vindas** personalizada
- **Resumo dos dados** cadastrados
- **Instruções passo a passo** para usar o sistema
- **Botão de acesso direto** ao sistema
- **Informações de suporte** e contato

## 🧪 Testes

### Teste Automático

```bash
cd backend
python scripts/teste_email_cadastro.py
```

### Teste Manual

1. Configure o arquivo `.env`
2. Inicie o servidor: `python -m uvicorn app.main:app --reload`
3. Acesse: `http://localhost:8000/cadastro.html`
4. Preencha o formulário de cadastro
5. Verifique se recebeu o e-mail de confirmação

## 🔧 Troubleshooting

### E-mail não é enviado

**Verifique:**
- ✅ Arquivo `.env` existe e está configurado corretamente
- ✅ Todas as variáveis de ambiente estão definidas
- ✅ Senha de app do Gmail está correta
- ✅ Servidor está rodando

**Logs:**
```bash
# Verificar logs do servidor
tail -f logs/app.log
```

### E-mail vai para spam

**Soluções:**
- Adicione `equipesensorium@gmail.com` aos seus contatos
- Verifique a pasta de spam/lixo eletrônico
- Configure o Gmail para não marcar como spam

### Erro de autenticação

**Para Gmail:**
- Certifique-se de usar uma senha de app, não a senha normal
- Verifique se a autenticação de dois fatores está habilitada
- Gere uma nova senha de app se necessário

## 📱 Template do E-mail

O e-mail utiliza um template HTML responsivo que inclui:

- **Design moderno** com cores do Sensorium
- **Layout responsivo** para desktop e mobile
- **Emojis e ícones** para melhor visualização
- **Seções organizadas** com informações claras
- **Botões de ação** para facilitar navegação

## 🔒 Segurança

- **Não armazenamos senhas** em texto plano
- **E-mails são enviados de forma segura** via SMTP/TLS
- **Dados sensíveis** são protegidos
- **Logs de erro** não expõem informações confidenciais

## 📞 Suporte

Em caso de problemas:

- **E-mail:** equipesensorium@gmail.com
- **Documentação:** Consulte os guias na pasta `docs/`
- **Logs:** Verifique os logs do servidor para erros específicos

## 🎯 Próximos Passos

Após configurar o sistema de e-mail:

1. **Teste o cadastro** de um usuário real
2. **Verifique se o e-mail** é recebido corretamente
3. **Configure notificações** adicionais se necessário
4. **Monitore os logs** para garantir funcionamento

---

**Equipe Sensorium UFRPE** 🌊  
*Sistema de Monitoramento de Qualidade da Água*
