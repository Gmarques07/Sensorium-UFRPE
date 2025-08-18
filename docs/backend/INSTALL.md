# Guia de Instalação - Sensorium UFRPE

Este guia fornece instruções detalhadas para instalar e configurar o sistema Sensorium UFRPE.

## Requisitos do Sistema

### Software Necessário
- Python 3.8 ou superior
- PostgreSQL 12 ou superior
- Git

### Hardware Recomendado
- CPU: 2 cores ou mais
- RAM: 4GB ou mais
- Armazenamento: 10GB de espaço livre

## Instalação

### 1. Preparação do Ambiente

#### Windows
```powershell
# Instalar Python (caso não tenha)
# Baixe do site oficial: https://www.python.org/downloads/

# Instalar PostgreSQL
# Baixe do site oficial: https://www.postgresql.org/download/windows/

# Verificar instalação do Python
python --version

# Verificar instalação do pip
pip --version
```

#### Linux (Ubuntu/Debian)
```bash
# Atualizar pacotes
sudo apt update
sudo apt upgrade

# Instalar Python e pip
sudo apt install python3.8 python3-pip

# Instalar PostgreSQL
sudo apt install postgresql postgresql-contrib

# Verificar instalações
python3 --version
pip3 --version
psql --version
```

### 2. Configuração do Banco de Dados

```sql
-- Conectar ao PostgreSQL
psql -U postgres

-- Criar banco de dados
CREATE DATABASE sensorium;

-- Criar usuário
CREATE USER sensorium_user WITH PASSWORD 'sua_senha';

-- Conceder privilégios
GRANT ALL PRIVILEGES ON DATABASE sensorium TO sensorium_user;
```

### 3. Instalação do Projeto

```powershell
# Clonar o repositório
git clone https://github.com/Gmarques07/Sensorium-UFRPE.git
cd Sensorium-UFRPE/backend

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 4. Configuração do Ambiente

Crie um arquivo `.env` na pasta `backend/` com as seguintes variáveis:

```env
# Configurações do Banco de Dados
DATABASE_URL=postgresql://sensorium_user:sua_senha@localhost:5432/sensorium

# Configurações de Segurança
SECRET_KEY=sua_chave_secreta_muito_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configurações do Servidor
HOST=0.0.0.0
PORT=8000
RELOAD=True
WORKERS=4

# Configurações de Email (opcional)
MAIL_USERNAME=seu_email@gmail.com
MAIL_PASSWORD=sua_senha_do_app
MAIL_FROM=seu_email@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_TLS=True
MAIL_SSL=False
```

### 5. Inicialização do Sistema

```powershell
# Aplicar migrações do banco de dados
alembic upgrade head

# Iniciar o servidor
uvicorn app:app --reload
```

O servidor estará disponível em: http://localhost:8000

## Verificação da Instalação

1. Acessar a documentação: http://localhost:8000/docs
2. Testar o endpoint de saúde: http://localhost:8000/health
3. Tentar fazer login com as credenciais padrão:
   - Email: admin@sensorium.com
   - Senha: admin123

## Configurações Avançadas

### Configuração do Nginx (Produção)

```nginx
server {
    listen 80;
    server_name seu_dominio.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Configuração do Supervisor (Produção)

```ini
[program:sensorium]
command=/caminho/para/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
directory=/caminho/para/backend
user=seu_usuario
autostart=true
autorestart=true
stderr_logfile=/var/log/sensorium.err.log
stdout_logfile=/var/log/sensorium.out.log
```

### Configuração do SSL/HTTPS

1. Instalar Certbot
2. Obter certificado SSL
3. Configurar Nginx com SSL

## Solução de Problemas

### Problemas Comuns

1. **Erro de Conexão com Banco de Dados**
   - Verificar se PostgreSQL está rodando
   - Confirmar credenciais no .env
   - Verificar permissões do usuário

2. **Erro ao Iniciar Servidor**
   - Verificar se porta 8000 está livre
   - Confirmar ambiente virtual ativo
   - Verificar logs de erro

3. **Problemas de Permissão**
   - Verificar permissões de arquivos
   - Confirmar usuário do processo
   - Verificar SELinux (Linux)

### Logs e Depuração

- Logs do aplicativo: `logs/app.log`
- Logs do Nginx: `/var/log/nginx/`
- Logs do PostgreSQL: `/var/log/postgresql/`

## Suporte

Para suporte técnico:
- Email: suporte@sensorium.com
- Issues: GitHub
- Documentação: `/docs`
