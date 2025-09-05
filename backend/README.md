# Backend Sensorium UFRPE - FastAPI

## Visão Geral

Este é o backend do sistema Sensorium UFRPE, implementado com FastAPI, um framework web moderno e de alta performance para construir APIs com Python 3.7+ baseado em type hints.

## Estrutura do Projeto

```
/backend
├── app/                    # Aplicação principal
│   ├── api/               # Endpoints da API
│   │   ├── deps.py        # Dependências da API
│   │   └── v1/            # Versão 1 da API
│   │       ├── endpoints/ # Endpoints individuais
│   │       └── __init__.py # Configuração dos routers
│   ├── core/              # Configurações e segurança
│   ├── crud/              # Operações do banco de dados
│   ├── db/                # Configuração do banco de dados
│   ├── models/            # Modelos do SQLAlchemy
│   ├── schemas/           # Schemas do Pydantic
│   └── main.py           # Configuração principal da aplicação
├── config/                # Arquivos de configuração
│   ├── .env.example       # Exemplo de arquivo de configuração
│   ├── docker-compose.yml # Configuração do Docker
│   ├── Dockerfile         # Imagem do Docker
│   └── requirements.txt   # Dependências do projeto
├── scripts/               # Scripts de utilidade
│   ├── init_db.py         # Script para inicializar o banco de dados
│   ├── start_server.py    # Script para iniciar o servidor
│   ├── run_tests.sh       # Script interativo para testes (Linux/macOS)
│   ├── run_tests.bat      # Script interativo para testes (Windows)
│   ├── run_tests.ps1      # Script PowerShell para testes (Windows)
│   └── test.sh            # Script de comandos diretos para testes (Linux/macOS)
├── static/               # Arquivos estáticos
├── templates/            # Templates HTML
├── docs/                 # Documentação
│   ├── README.md         # Este arquivo
│   └── INSTALACAO.md     # Instruções de instalação
└── tests/                # Testes automatizados
    ├── integration/      # Testes de integração
    └── unitários/        # Testes unitários
```

## Tecnologias Utilizadas

- **FastAPI**: Framework web moderno e rápido
- **SQLAlchemy**: ORM para Python
- **Pydantic**: Validação de dados usando type hints
- **JWT**: Autenticação com tokens
- **MySQL**: Banco de dados relacional
- **Uvicorn**: Servidor ASGI para produção

## Pré-requisitos

1. **Python 3.7+**
2. **MySQL Server** (instalado e em execução)
3. **pip** (gerenciador de pacotes do Python)

## Instalação

1. Navegue até o diretório do backend:
   ```bash
   cd backend
   ```

2. Crie um ambiente virtual (opcional mas recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r config/requirements.txt
   ```

4. Configure o ambiente:
   ```bash
   cp config/.env.example .env
   ```
   Edite o arquivo `.env` com as configurações do seu banco de dados.

5. Verifique a conexão com o MySQL:
   ```bash
   python scripts/test_local_connect.py
   ```

6. Inicialize o banco de dados:
   ```bash
   python scripts/init_db.py
   ```

## Configuração do Banco de Dados MySQL

### 1. Instalar o MySQL Server

**Windows:**
- Baixe o MySQL Installer do site oficial
- Siga as instruções de instalação

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql
```

**macOS:**
```bash
brew install mysql
brew services start mysql
```

### 2. Configurar o usuário e banco de dados

Após instalar o MySQL, conecte-se como root:
```bash
mysql -u root -p
```

Execute os seguintes comandos SQL:
```sql
CREATE DATABASE IF NOT EXISTS sensorium_db;
CREATE USER 'sensorium_user'@'localhost' IDENTIFIED BY 'sensorium_password';
GRANT ALL PRIVILEGES ON sensorium_db.* TO 'sensorium_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. Atualizar o arquivo .env

Edite o arquivo `.env` com as configurações corretas:
```
MYSQL_USER=sensorium_user
MYSQL_PASSWORD=sensorium_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=sensorium_db
```

## Executando o Servidor

### Para desenvolvimento:
```bash
python scripts/start_server.py --reload
```

### Para produção:
```bash
python scripts/start_server.py
```

O servidor estará disponível em `http://localhost:8000`

## Documentação da API

A documentação automática da API está disponível em:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Estrutura das Rotas

- **Autenticação**: `/api/v1/auth/`
- **Usuários**: `/api/v1/usuarios/`
- **Administração**: `/api/v1/admin/`
- **Locais**: `/api/v1/locais/`
- **Notificações**: `/api/v1/notificacoes/`

## Contribuindo

1. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
2. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
3. Push para a branch (`git push origin feature/AmazingFeature`)
4. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT.

## 🐳 Docker

### Início Rápido com Docker

```bash
cd backend
docker-compose -f config/docker-compose.yml up -d --build
```

**Acesse**: http://localhost:8001

### Comandos Úteis

```bash
# Iniciar serviços
docker-compose -f config/docker-compose.yml up -d

# Parar serviços
docker-compose -f config/docker-compose.yml down

# Ver logs
docker-compose -f config/docker-compose.yml logs -f backend

# Rebuild
docker-compose -f config/docker-compose.yml up -d --build

# Executar comandos no container
docker-compose -f config/docker-compose.yml exec backend bash
```

### Configuração

O Docker está configurado para usar o MySQL local do seu sistema:

- **Host**: `host.docker.internal` (acessa MySQL local)
- **Porta**: `3306`
- **Usuário**: `root`
- **Senha**: (vazia - ajuste no config/docker-compose.yml se necessário)
- **Banco**: `banco_de_dados`

### Personalização

Edite o `config/docker-compose.yml` para ajustar:
- Credenciais do banco de dados
- Porta do servidor
- Variáveis de ambiente
- Volumes montados

### Troubleshooting

**Problema**: Container não inicia
- Verifique se o MySQL está rodando localmente
- Confirme as credenciais no config/docker-compose.yml
- Verifique os logs: `docker-compose -f config/docker-compose.yml logs backend`

**Problema**: Porta já em uso
- Pare outros serviços na porta 8001
- Ou altere a porta no config/docker-compose.yml

## 🧪 Testes Automatizados

O projeto inclui scripts para facilitar a execução dos testes automatizados usando Docker:

### Scripts Disponíveis

- `scripts/run_tests.sh` - Script interativo para Linux/macOS
- `scripts/run_tests.bat` - Script interativo para Windows
- `scripts/run_tests.ps1` - Script PowerShell para Windows
- `scripts/test.sh` - Script de comandos diretos para Linux/macOS

### Exemplos de Uso

```bash
# Linux/macOS
cd backend
./scripts/run_tests.sh        # Interface interativa
./scripts/test.sh all         # Executar todos os testes
./scripts/test.sh unit        # Apenas testes de unidade
./scripts/test.sh integration # Apenas testes de integração

# Windows (CMD)
cd backend
scripts\run_tests.bat

# Windows (PowerShell)
cd backend
.\scripts\run_tests.ps1
```

### Comandos Diretos do Docker

```bash
# Executar testes de unidade
docker-compose -f config/docker-compose.yml run --rm tests

# Executar testes de integração
docker-compose -f config/docker-compose.yml run --rm tests_integration

# Executar testes com cobertura
docker-compose -f config/docker-compose.yml run --rm tests pytest --cov=app --cov-report=term-missing
```

## 📁 Estrutura de Pastas

O projeto foi organizado em pastas para melhor manutenção e escalabilidade. Veja mais detalhes em [docs/ESTRUTURA_DE_PASTAS.md](docs/ESTRUTURA_DE_PASTAS.md).

> 📖 **Guias Completos**: 
> - [docs/INSTALACAO.md](docs/INSTALACAO.md) - Instruções detalhadas de instalação
> - [docs/ESTRUTURA_DE_PASTAS.md](docs/ESTRUTURA_DE_PASTAS.md) - Estrutura de pastas do projeto