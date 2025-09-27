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