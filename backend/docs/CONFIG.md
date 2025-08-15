# Configurações do Sistema - Sensorium UFRPE

Este documento detalha todas as configurações disponíveis no sistema Sensorium UFRPE.

## Variáveis de Ambiente

### Banco de Dados
```env
# URL de conexão com o PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Pool de conexões
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
```

### Segurança
```env
# Chave secreta para JWT
SECRET_KEY=sua_chave_secreta

# Configurações JWT
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Configurações de senha
MIN_PASSWORD_LENGTH=8
PASSWORD_REQUIRE_SPECIAL=True
PASSWORD_REQUIRE_NUMBERS=True
```

### Servidor
```env
# Configurações do servidor
HOST=0.0.0.0
PORT=8000
RELOAD=True
WORKERS=4
LOG_LEVEL=info

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "https://sensorium.com"]
ALLOWED_METHODS=["*"]
ALLOWED_HEADERS=["*"]
```

### Email
```env
# Servidor SMTP
MAIL_USERNAME=seu_email@gmail.com
MAIL_PASSWORD=sua_senha
MAIL_FROM=seu_email@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_TLS=True
MAIL_SSL=False

# Templates de email
EMAIL_TEMPLATES_DIR=app/templates/email
```

### Cache
```env
# Redis
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=senha
REDIS_DB=0

# Configurações de cache
CACHE_TTL=3600
CACHE_PREFIX=sensorium:
```

### Monitoramento
```env
# Sentry
SENTRY_DSN=https://seu-dsn.sentry.io

# Métricas
ENABLE_METRICS=True
METRICS_PORT=9090
```

## Arquivos de Configuração

### 1. logging.conf
```ini
[loggers]
keys=root,app

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_app]
level=INFO
handlers=fileHandler
qualname=app
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=INFO
formatter=simpleFormatter
args=('logs/app.log', 'a')

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### 2. alembic.ini
```ini
[alembic]
script_location = migrations
sqlalchemy.url = driver://user:pass@localhost/dbname

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic
```

### 3. uvicorn.json
```json
{
    "host": "0.0.0.0",
    "port": 8000,
    "reload": true,
    "workers": 4,
    "log_level": "info",
    "proxy_headers": true,
    "forwarded_allow_ips": "*"
}
```

## Configurações de Produção

### 1. nginx.conf
```nginx
server {
    listen 80;
    server_name sensorium.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /path/to/static;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
}
```

### 2. supervisor.conf
```ini
[program:sensorium]
command=/path/to/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/sensorium.err.log
stdout_logfile=/var/log/sensorium.out.log
```

## Configurações do Sistema

### 1. Limites de Taxa
```python
RATE_LIMIT_CONFIG = {
    "default": "100/minute",
    "login": "5/minute",
    "signup": "3/minute",
    "api": "1000/hour"
}
```

### 2. Configurações de Upload
```python
UPLOAD_CONFIG = {
    "max_size": 5_000_000,  # 5MB
    "allowed_types": ["image/jpeg", "image/png", "application/pdf"],
    "upload_dir": "uploads/"
}
```

### 3. Configurações de Notificação
```python
NOTIFICATION_CONFIG = {
    "enable_email": True,
    "enable_push": False,
    "notification_check_interval": 300,  # 5 minutos
    "batch_size": 100
}
```

## Personalização

### 1. Temas
```python
THEME_CONFIG = {
    "primary_color": "#007bff",
    "secondary_color": "#6c757d",
    "success_color": "#28a745",
    "danger_color": "#dc3545",
    "warning_color": "#ffc107",
    "info_color": "#17a2b8"
}
```

### 2. Logos e Imagens
```python
BRAND_CONFIG = {
    "logo_path": "static/img/logo.png",
    "favicon_path": "static/img/favicon.ico",
    "default_avatar": "static/img/default_avatar.png"
}
```

## Segurança Adicional

### 1. Configurações CSP
```python
CSP_CONFIG = {
    "default-src": ["'self'"],
    "script-src": ["'self'", "'unsafe-inline'"],
    "style-src": ["'self'", "'unsafe-inline'"],
    "img-src": ["'self'", "data:", "https:"],
    "connect-src": ["'self'"]
}
```

### 2. Configurações de Backup
```python
BACKUP_CONFIG = {
    "enable_auto_backup": True,
    "backup_interval": 86400,  # 24 horas
    "backup_retention": 30,    # 30 dias
    "backup_path": "/path/to/backups"
}
```
