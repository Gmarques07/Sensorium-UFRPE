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
├── static/               # Arquivos estáticos
├── templates/            # Templates HTML
├── init_db.py            # Script para inicializar o banco de dados
├── main.py               # Ponto de entrada da aplicação
├── start_server.py       # Script para iniciar o servidor
├── check_mysql.py        # Script para verificar conexão com MySQL
├── requirements.txt      # Dependências do projeto
└── .env.example         # Exemplo de arquivo de configuração
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
   pip install -r requirements.txt
   ```

4. Configure o ambiente:
   ```bash
   cp .env.example .env
   ```
   Edite o arquivo `.env` com as configurações do seu banco de dados.

5. Verifique a conexão com o MySQL:
   ```bash
   python check_mysql.py
   ```

6. Inicialize o banco de dados:
   ```bash
   python init_db.py
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
python start_server.py --reload
```

### Para produção:
```bash
python start_server.py
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