# Estrutura de Pastas do Backend

Este documento descreve a organização de pastas do backend do projeto Sensorium UFRPE.

## Estrutura Atual

```
/backend
├── app/                    # Aplicação principal
│   ├── api/               # Endpoints da API
│   ├── core/              # Configurações e segurança
│   ├── crud/              # Operações do banco de dados
│   ├── db/                # Configuração do banco de dados
│   ├── models/            # Modelos do SQLAlchemy
│   ├── schemas/           # Schemas do Pydantic
│   └── main.py           # Configuração principal da aplicação
├── config/                # Arquivos de configuração
│   ├── .env.example       # Exemplo de arquivo de configuração
│   ├── .env.railway       # Configuração para Railway
│   ├── docker-compose.yml # Configuração do Docker Compose
│   ├── Dockerfile         # Imagem do Docker
│   └── requirements.txt   # Dependências do projeto
├── scripts/               # Scripts de utilidade
│   ├── init_db.py         # Script para inicializar o banco de dados
│   ├── start_server.py    # Script para iniciar o servidor
│   ├── install.py         # Script de instalação
│   ├── recreate_db.py     # Script para recriar o banco de dados
│   ├── auth_script.js     # Script de autenticação
│   ├── test_local_connect.py # Script para testar conexão local
│   ├── run_tests.sh       # Script interativo para testes (Linux/macOS)
│   ├── run_tests.bat      # Script interativo para testes (Windows)
│   ├── run_tests.ps1      # Script PowerShell para testes (Windows)
│   └── test.sh            # Script de comandos diretos para testes (Linux/macOS)
├── static/                # Arquivos estáticos
├── templates/             # Templates HTML
├── docs/                  # Documentação
│   ├── README.md          # Documentação principal
│   └── INSTALACAO.md      # Instruções de instalação
├── tests/                 # Testes automatizados
│   ├── integration/       # Testes de integração
│   └── unit/              # Testes unitários (na raiz de tests)
└── README.md             # Documentação principal na raiz do backend
```

## Descrição das Pastas

### app/
Contém toda a lógica da aplicação FastAPI, incluindo:
- Endpoints da API
- Modelos de dados
- Schemas Pydantic
- Operações CRUD
- Configurações de segurança

### config/
Contém todos os arquivos de configuração do projeto:
- Arquivos .env para variáveis de ambiente
- Configuração do Docker (Dockerfile, docker-compose.yml)
- Dependências do projeto (requirements.txt)

### scripts/
Contém scripts utilitários para várias tarefas:
- Inicialização do banco de dados
- Início do servidor
- Testes automatizados
- Conexão com o banco de dados

### static/
Contém arquivos estáticos como CSS, JavaScript, imagens, etc.

### templates/
Contém templates HTML para renderização no servidor.

### docs/
Contém documentação do projeto:
- README principal
- Instruções de instalação
- Guias de uso

### tests/
Contém todos os testes automatizados:
- Testes unitários na raiz da pasta
- Testes de integração na subpasta integration

## Como Usar

### Para desenvolvimento:
```bash
cd backend
python scripts/start_server.py --reload
```

### Para executar testes:
```bash
cd backend/scripts
./run_tests.sh        # Linux/macOS
run_tests.bat         # Windows (CMD)
.\run_tests.ps1       # Windows (PowerShell)
```

### Com Docker:
```bash
cd backend
docker-compose -f config/docker-compose.yml up -d --build
```