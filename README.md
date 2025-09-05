# 🌊 Sistema Sensorium UFRPE

Sistema web moderno para gerenciamento de cisternas, monitoramento de níveis de água e qualidade (pH). Desenvolvido com FastAPI e interface responsiva para usuários, empresas e administradores.

## 🚀 Início Rápido

### Opção 1: Docker (Recomendado para iniciantes)
```bash
git clone [URL_DO_REPOSITORIO]
cd Sensorium-UFRPE/backend
docker-compose up -d --build
```
**Acesse**: http://localhost:8001

### Opção 2: Instalação Local
```bash
git clone [URL_DO_REPOSITORIO]
cd Sensorium-UFRPE/backend
pip install -r requirements.txt
python init_db.py
python start_server.py --reload
```
**Acesse**: http://localhost:8000

> 📖 **Guias Completos**: 
> - [Início Rápido](docs/guides/QUICK_START.md) - Escolha entre Docker ou Local
> - [Guia Docker](docs/guides/DOCKER_GUIDE.md) - Instruções detalhadas para Docker
> - [Guia de Testes](docs/guides/TESTS_GUIDE.md) - Documentação completa dos testes

## ✨ Funcionalidades Principais

### 👥 Para Usuários
- ✅ Cadastro e login seguro
- 📊 Dashboard com monitoramento em tempo real
- 📈 Visualização de níveis de água e pH
- 📱 Interface responsiva e moderna
- 🔔 Sistema de notificações
- 📋 Histórico de leituras dos sensores

### 🏢 Para Empresas
- 🔐 Painel administrativo
- 📊 Monitoramento de múltiplas cisternas
- 👥 Gerenciamento de usuários
- 📈 Relatórios e análises
- 🔔 Sistema de notificações

### ⚙️ Para Administradores
- 🛠️ Painel administrativo completo
- 👥 Gerenciamento de usuários e empresas
- 📊 Estatísticas do sistema
- ⚙️ Configurações avançadas
- 🔒 Controle de acesso

## 🛠️ Tecnologias Utilizadas

### Backend
- **FastAPI** - Framework web moderno e assíncrono
- **SQLAlchemy** - ORM para Python
- **Pydantic** - Validação de dados
- **JWT** - Autenticação segura
- **MySQL** - Banco de dados relacional
- **Uvicorn** - Servidor ASGI

### Frontend
- **HTML5/CSS3/JavaScript** - Base da interface
- **Bootstrap 5** - Framework CSS responsivo
- **Chart.js** - Gráficos interativos
- **Jinja2** - Templates dinâmicos

### DevOps
- **Docker** - Containerização
- **Docker Compose** - Orquestração de serviços

## 📋 Pré-requisitos

### Para Docker (Recomendado)
- Docker Desktop (Windows/Mac) ou Docker Engine (Linux)
- Docker Compose
- MySQL local (WAMP/XAMPP/LAMP)

### Para Instalação Local
- Python 3.7+
- MySQL Server
- pip (gerenciador de pacotes Python)

## 🔧 Instalação Detalhada

### Método 1: Docker (Mais Fácil)

1. **Clone o repositório**:
```bash
git clone [URL_DO_REPOSITORIO]
cd Sensorium-UFRPE
```

2. **Execute com Docker**:
```bash
cd backend
docker-compose up -d --build
```

3. **Acesse o sistema**:
- Frontend: http://localhost:8001
- API Docs: http://localhost:8001/docs

### Configuração de E-mails

Para habilitar o envio de relatórios por e-mail, consulte o arquivo `CONFIG_EMAIL.md` para instruções detalhadas sobre como configurar as variáveis de ambiente necessárias.

### Método 2: Instalação Local

1. **Clone e navegue**:
```bash
git clone [URL_DO_REPOSITORIO]
cd Sensorium-UFRPE/backend
```

2. **Configure o ambiente**:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Instale dependências**:
```bash
pip install -r requirements.txt
```

4. **Configure o banco e e-mails**:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
# Veja CONFIG_EMAIL.md para instruções sobre configuração de e-mails
python init_db.py
```

5. **Inicie o servidor**:
```bash
python start_server.py --reload
```

## 📁 Estrutura do Projeto

```
Sensorium-UFRPE/
├── 📁 backend/                 # Backend FastAPI
│   ├── 📁 app/                # Aplicação principal
│   │   ├── 📁 api/            # Endpoints da API
│   │   ├── 📁 core/           # Configurações e segurança
│   │   ├── 📁 crud/           # Operações do banco
│   │   ├── 📁 models/         # Modelos SQLAlchemy
│   │   ├── 📁 schemas/        # Schemas Pydantic
│   │   └── main.py           # Configuração principal
│   ├── 📁 static/            # Arquivos estáticos
│   ├── 📁 templates/         # Templates HTML
│   ├── 📁 tests/             # Testes automatizados
│   ├── Dockerfile           # Imagem Docker
│   ├── docker-compose.yml   # Orquestração Docker
│   ├── start_server.py      # Script de inicialização
│   ├── env.example         # Exemplo de configuração
│   └── requirements.txt     # Dependências Python
├── 📁 templates/            # Templates compartilhados
├── 📁 static/              # Arquivos estáticos compartilhados
├── 📁 docs/               # Documentação organizada
│   ├── 📁 guides/         # Guias de uso
│   │   ├── QUICK_START.md
│   │   ├── DOCKER_GUIDE.md
│   │   └── DEVELOPER_GUIDE.md
│   ├── 📁 examples/       # Exemplos de configuração
│   │   └── env.example
│   └── DOCUMENTATION_SUMMARY.md
└── 📄 README.md           # Este arquivo
```

## 🌐 Acesso ao Sistema

### URLs Principais
- **Frontend**: http://localhost:8001 (Docker) ou http://localhost:8000 (Local)
- **API Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

### Contas de Teste
- **Usuário**: Crie uma conta através do cadastro
- **Admin**: Configure através do painel administrativo

## 📚 Documentação

- **[Início Rápido](docs/guides/QUICK_START.md)** - Escolha entre Docker ou Local
- **[Guia Docker Completo](docs/guides/DOCKER_GUIDE.md)** - Instruções detalhadas para Docker
- **[Guia do Desenvolvedor](docs/guides/DEVELOPER_GUIDE.md)** - Informações técnicas para desenvolvedores
- **[Backend README](backend/README.md)** - Documentação técnica do backend
- **[Resumo da Documentação](docs/DOCUMENTATION_SUMMARY.md)** - Índice completo de toda a documentação
- **[API Docs](http://localhost:8001/docs)** - Documentação interativa da API

## 🔒 Segurança

- ✅ Autenticação JWT
- ✅ Senhas criptografadas com bcrypt
- ✅ Validação de dados com Pydantic
- ✅ CORS configurado
- ✅ Rate limiting implementado
- ✅ Controle de acesso baseado em perfis

## 🚀 Deploy

## 🧪 Testes

O sistema possui uma suíte completa de testes automatizados:

### Testes de Unidade (20 testes)
- Autenticação e autorização
- Modelos de dados
- Endpoints da API
- Funções auxiliares

### Testes de Integração (10 testes)
- Fluxos completos do usuário
- Integração com banco de dados
- APIs REST completas

### Execução

```bash
# Docker (recomendado)
cd backend
docker-compose run --rm tests              # Testes de unidade
docker-compose run --rm tests_integration   # Testes de integração

# Local
cd backend
python -m pytest tests/ --ignore=tests/integration  # Testes de unidade
python -m pytest tests/integration/                 # Testes de integração
```

> 📖 **Documentação Completa**: [Guia de Testes](docs/guides/TESTS_GUIDE.md)

## 🚀 Deploy

### Docker (Produção)
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Local (Produção)
```bash
python start_server.py --host 0.0.0.0 --port 8000
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

- 📖 Consulte a [documentação](docs/guides/QUICK_START.md)
- 📚 [Resumo da Documentação](docs/DOCUMENTATION_SUMMARY.md) para encontrar informações específicas
- 🐳 [Guia Docker](docs/guides/DOCKER_GUIDE.md) para problemas específicos
- 👨‍💻 [Guia do Desenvolvedor](docs/guides/DEVELOPER_GUIDE.md) para informações técnicas
- 🧪 [Guia de Testes](docs/guides/TESTS_GUIDE.md) para informações sobre testes
- 🐛 Abra uma [issue](https://github.com/seu-repo/issues)
- 💬 Entre em contato com a equipe

---

**Desenvolvido com ❤️ pela equipe Sensorium UFRPE**

## Estrutura do Projeto

```
Sensorium-UFRPE/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       └── __init__.py
│   │   ├── core/
│   │   ├── crud/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── main.py
│   ├── static/
│   ├── templates/
│   ├── init_db.py
│   ├── main.py
│   ├── start_server.py
│   ├── check_mysql.py
│   ├── requirements.txt
│   └── .env.example
├── static/
├── templates/
├── ATUALIZACAO_MIGRACAO.md
├── MIGRACAO_FLASK_FASTAPI.md
├── README.md
└── requirements.txt
```

## Documentação da API

A documentação automática da API está disponível em:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Funcionalidades de Segurança

- Autenticação JWT
- Senhas criptografadas com bcrypt
- Controle de acesso baseado em perfis
- Validação de dados de entrada com Pydantic
- Proteção contra uploads maliciosos
- CORS configurado

## Processamento de Imagens

O sistema utiliza OpenCV para:
- Detecção automática de rachaduras
- Análise de objetos nas imagens
- Processamento e armazenamento seguro de uploads

## Contribuição

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## Suporte

Para suporte, abra uma issue no repositório ou consulte a documentação em `backend/README.md`.
