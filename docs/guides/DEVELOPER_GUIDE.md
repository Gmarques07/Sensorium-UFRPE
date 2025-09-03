# 👨‍💻 Guia do Desenvolvedor - Sistema Sensorium UFRPE

Este guia é destinado aos desenvolvedores que irão contribuir com o projeto, fornecendo informações técnicas detalhadas sobre a arquitetura, padrões de código e fluxo de desenvolvimento.

## 📋 Índice

- [Arquitetura do Sistema](#arquitetura-do-sistema)
- [Estrutura do Código](#estrutura-do-código)
- [Padrões de Desenvolvimento](#padrões-de-desenvolvimento)
- [Fluxo de Desenvolvimento](#fluxo-de-desenvolvimento)
- [Testes](#testes)
- [Deploy](#deploy)
- [Troubleshooting](#troubleshooting)

## 🏗️ Arquitetura do Sistema

### Visão Geral

O sistema utiliza uma arquitetura moderna baseada em:

- **Backend**: FastAPI (Python 3.7+)
- **Frontend**: HTML/CSS/JavaScript com Bootstrap
- **Banco de Dados**: MySQL
- **Autenticação**: JWT
- **Containerização**: Docker

### Diagrama de Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (HTML/JS)     │◄──►│   (FastAPI)     │◄──►│   (MySQL)       │
│   Port: 8001    │    │   Port: 8001    │    │   Port: 3306    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Templates     │    │   API Routes    │    │   Models        │
│   (Jinja2)      │    │   (Endpoints)   │    │   (SQLAlchemy)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Estrutura do Código

### Backend (FastAPI)

```
backend/
├── app/
│   ├── api/                    # Camada de API
│   │   ├── deps.py            # Dependências (auth, db)
│   │   └── v1/                # Versão 1 da API
│   │       ├── endpoints/     # Endpoints específicos
│   │       │   ├── auth.py    # Autenticação
│   │       │   ├── usuarios.py # Usuários
│   │       │   ├── admin.py   # Administração
│   │       │   └── local.py   # Locais/Sensores
│   │       └── __init__.py    # Configuração dos routers
│   ├── core/                  # Configurações centrais
│   │   ├── config.py          # Configurações do sistema
│   │   ├── security.py        # Segurança e JWT
│   │   └── limiter.py         # Rate limiting
│   ├── crud/                  # Operações do banco
│   │   ├── usuario.py         # CRUD de usuários
│   │   ├── admin.py           # CRUD de admin
│   │   └── local.py           # CRUD de locais
│   ├── db/                    # Configuração do banco
│   │   ├── database.py        # Conexão com banco
│   │   └── session.py         # Sessões do banco
│   ├── models/                # Modelos SQLAlchemy
│   │   ├── usuario.py         # Modelo de usuário
│   │   ├── admin.py           # Modelo de admin
│   │   └── local.py           # Modelo de local
│   ├── schemas/               # Schemas Pydantic
│   │   ├── usuario.py         # Schema de usuário
│   │   ├── auth.py            # Schema de autenticação
│   │   └── local.py           # Schema de local
│   └── main.py               # Aplicação principal
├── static/                   # Arquivos estáticos
├── templates/                # Templates HTML
├── tests/                    # Testes
├── Dockerfile               # Imagem Docker
├── docker-compose.yml       # Orquestração
└── requirements.txt         # Dependências
```

### Frontend

```
templates/
├── index.html               # Página inicial
├── login_usuario.html       # Login de usuário
├── login_admin.html         # Login de admin
├── cadastro.html            # Cadastro
├── dashboard_usuario.html   # Dashboard do usuário
├── admin_dashboard.html     # Dashboard do admin
└── ...

static/
├── css/
│   └── style.css           # Estilos customizados
└── js/
    └── script.js           # JavaScript customizado
```

## 🎯 Padrões de Desenvolvimento

### Convenções de Código

#### Python (Backend)
```python
# Nomes de arquivos: snake_case
# Exemplo: usuario_service.py

# Nomes de classes: PascalCase
class UsuarioService:
    pass

# Nomes de funções: snake_case
def criar_usuario():
    pass

# Nomes de variáveis: snake_case
usuario_id = 1

# Constantes: UPPER_CASE
MAX_RETRY_ATTEMPTS = 3
```

#### JavaScript (Frontend)
```javascript
// Nomes de variáveis: camelCase
const usuarioId = 1;

// Nomes de funções: camelCase
function criarUsuario() {
    // ...
}

// Nomes de constantes: UPPER_CASE
const MAX_RETRY_ATTEMPTS = 3;
```

### Estrutura de Endpoints

```python
@router.post(
    "/endpoint",
    response_model=SchemaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Descrição do endpoint",
    response_description="Descrição da resposta",
    tags=["categoria"]
)
async def nome_do_endpoint(
    dados: SchemaRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    """
    Docstring detalhada do endpoint.
    
    Args:
        dados: Dados de entrada
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        SchemaResponse: Resposta do endpoint
        
    Raises:
        HTTPException: Erros específicos
    """
    # Implementação
    pass
```

### Estrutura de CRUD

```python
def criar_entidade(db: Session, entidade: SchemaCreate) -> Model:
    """Cria uma nova entidade no banco de dados."""
    db_entidade = Model(**entidade.dict())
    db.add(db_entidade)
    db.commit()
    db.refresh(db_entidade)
    return db_entidade

def obter_entidade(db: Session, id: int) -> Optional[Model]:
    """Obtém uma entidade por ID."""
    return db.query(Model).filter(Model.id == id).first()

def listar_entidades(db: Session, skip: int = 0, limit: int = 100) -> List[Model]:
    """Lista entidades com paginação."""
    return db.query(Model).offset(skip).limit(limit).all()

def atualizar_entidade(db: Session, id: int, entidade: SchemaUpdate) -> Optional[Model]:
    """Atualiza uma entidade existente."""
    db_entidade = obter_entidade(db, id)
    if db_entidade:
        for key, value in entidade.dict(exclude_unset=True).items():
            setattr(db_entidade, key, value)
        db.commit()
        db.refresh(db_entidade)
    return db_entidade

def deletar_entidade(db: Session, id: int) -> bool:
    """Deleta uma entidade."""
    db_entidade = obter_entidade(db, id)
    if db_entidade:
        db.delete(db_entidade)
        db.commit()
        return True
    return False
```

## 🔄 Fluxo de Desenvolvimento

### 1. Configuração do Ambiente

```bash
# Clone o repositório
git clone [URL_DO_REPOSITORIO]
cd Sensorium-UFRPE

# Escolha o ambiente
# Opção A: Docker
cd backend
docker-compose up -d --build

# Opção B: Local
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
python init_db.py
python start_server.py --reload
```

### 2. Criação de Features

```bash
# Crie uma branch para sua feature
git checkout -b feature/nova-funcionalidade

# Desenvolva sua feature
# ... código ...

# Teste sua feature
python -m pytest tests/

# Commit suas mudanças
git add .
git commit -m "feat: adiciona nova funcionalidade"

# Push para o repositório
git push origin feature/nova-funcionalidade
```

### 3. Pull Request

1. Abra um Pull Request no GitHub
2. Descreva as mudanças realizadas
3. Aguarde a revisão do código
4. Faça as correções solicitadas
5. Merge após aprovação

## 🧪 Testes

### Estrutura de Testes

```
tests/
├── conftest.py              # Configuração dos testes
├── test_auth.py             # Testes de autenticação
├── test_usuarios.py         # Testes de usuários
├── test_admin.py            # Testes de admin
├── test_local.py            # Testes de locais
└── test_basic.py            # Testes básicos
```

### Executando Testes

```bash
# Todos os testes
python -m pytest

# Testes específicos
python -m pytest tests/test_auth.py

# Testes com cobertura
python -m pytest --cov=app tests/

# Testes com verbose
python -m pytest -v
```

### Exemplo de Teste

```python
def test_criar_usuario(client, db):
    """Testa a criação de um novo usuário."""
    dados = {
        "nome": "João Silva",
        "email": "joao@example.com",
        "cpf": "12345678900",
        "senha": "senha123"
    }
    
    response = client.post("/api/v1/auth/registro", json=dados)
    
    assert response.status_code == 201
    assert response.json()["access_token"] is not None
```

## 🚀 Deploy

### Desenvolvimento

```bash
# Docker
docker-compose up -d

# Local
python start_server.py --reload
```

### Produção

```bash
# Docker
docker-compose -f docker-compose.prod.yml up -d

# Local
python start_server.py --host 0.0.0.0 --port 8000
```

### Variáveis de Ambiente para Produção

```env
# Produção
ENVIRONMENT=production
SECRET_KEY=chave_super_secreta_producao
MYSQL_HOST=banco_producao
MYSQL_PASSWORD=senha_forte
BACKEND_CORS_ORIGINS=["https://seu-dominio.com"]
```

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Erro de Importação
```python
# Erro
ModuleNotFoundError: No module named 'app'

# Solução
# Certifique-se de que está no diretório correto
cd backend
python -m app.main
```

#### 2. Erro de Banco de Dados
```python
# Erro
sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError)

# Solução
# Verifique se o MySQL está rodando
# Confirme as credenciais no .env
python check_mysql.py
```

#### 3. Erro de CORS
```python
# Erro
Access to fetch at 'http://localhost:8000' from origin 'http://localhost:3000' has been blocked by CORS policy

# Solução
# Adicione a origem no BACKEND_CORS_ORIGINS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

### Debugging

#### Logs do Sistema
```bash
# Docker
docker-compose logs -f backend

# Local
# Os logs aparecem no terminal onde o servidor está rodando
```

#### Debug no Código
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Ou use o debugger
import pdb; pdb.set_trace()
```

## 📚 Recursos Úteis

### Documentação do Projeto
- [Resumo da Documentação](DOCUMENTATION_SUMMARY.md) - Índice completo de toda a documentação
- [Guia Docker](DOCKER_GUIDE.md) - Instruções detalhadas para Docker
- [Início Rápido](QUICK_START.md) - Guia de início rápido

### Documentação Externa
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Pydantic Docs](https://pydantic-docs.helpmanual.io/)
- [Docker Docs](https://docs.docker.com/)

### Ferramentas
- **VS Code** com extensões Python e Docker
- **Postman** para testar APIs
- **MySQL Workbench** para gerenciar banco
- **Git** para controle de versão

### Comandos Úteis

```bash
# Git
git status
git log --oneline
git diff

# Docker
docker ps
docker logs [container_id]
docker exec -it [container_id] bash

# Python
python -m pip list
python -m pip freeze > requirements.txt
python -c "import sys; print(sys.path)"
```

### Troubleshooting Rápido

```bash
# Verificar se o servidor está rodando
curl http://localhost:8001/health

# Verificar logs do Docker
docker-compose logs -f backend

# Verificar conexão com banco
python check_mysql.py

# Executar testes
python -m pytest tests/
```

### Próximos Passos

1. **Configure seu ambiente** seguindo o [Início Rápido](QUICK_START.md)
2. **Leia a [documentação técnica](backend/README.md)** do backend
3. **Explore os [exemplos de código](DEVELOPER_GUIDE.md)** neste guia
4. **Execute os testes** para verificar se tudo está funcionando
5. **Comece a desenvolver** sua primeira feature

### Recursos Adicionais

- **[Resumo da Documentação](DOCUMENTATION_SUMMARY.md)** - Índice completo de toda a documentação
- **[Guia Docker](DOCKER_GUIDE.md)** - Para problemas específicos do Docker
- **[Início Rápido](QUICK_START.md)** - Para configuração inicial
- **[Backend README](backend/README.md)** - Documentação técnica específica

### Documentação Externa

- **[FastAPI Docs](https://fastapi.tiangolo.com/)** - Documentação oficial do FastAPI
- **[SQLAlchemy Docs](https://docs.sqlalchemy.org/)** - Documentação oficial do SQLAlchemy
- **[Pydantic Docs](https://pydantic-docs.helpmanual.io/)** - Documentação oficial do Pydantic
- **[Docker Docs](https://docs.docker.com/)** - Documentação oficial do Docker

## 🤝 Contribuindo

### Antes de Contribuir

1. **Leia a documentação** completa
2. **Consulte o [Resumo da Documentação](DOCUMENTATION_SUMMARY.md)** para encontrar informações específicas
3. **Configure o ambiente** de desenvolvimento
4. **Execute os testes** para garantir que tudo funciona
5. **Crie uma branch** para sua feature
6. **Siga os padrões** de código estabelecidos

### Checklist de Pull Request

- [ ] Código segue os padrões estabelecidos
- [ ] Testes passam
- [ ] Documentação atualizada
- [ ] Commits bem descritos
- [ ] Branch atualizada com main
- [ ] [Resumo da Documentação](DOCUMENTATION_SUMMARY.md) atualizado se necessário

## 🆘 Suporte

### Para Desenvolvedores

1. **Consulte o [Resumo da Documentação](DOCUMENTATION_SUMMARY.md)** para encontrar informações específicas
2. **Verifique os logs** do sistema
3. **Execute os testes** para identificar problemas
4. **Abra uma issue** no repositório
5. **Entre em contato** com a equipe

### Recursos de Ajuda

- **[Resumo da Documentação](DOCUMENTATION_SUMMARY.md)** - Índice completo de toda a documentação
- **[Guia Docker](DOCKER_GUIDE.md)** - Para problemas específicos do Docker
- **[Início Rápido](QUICK_START.md)** - Para configuração inicial
- **[Backend README](backend/README.md)** - Documentação técnica específica

### Documentação Externa

- **[FastAPI Docs](https://fastapi.tiangolo.com/)** - Documentação oficial do FastAPI
- **[SQLAlchemy Docs](https://docs.sqlalchemy.org/)** - Documentação oficial do SQLAlchemy
- **[Pydantic Docs](https://pydantic-docs.helpmanual.io/)** - Documentação oficial do Pydantic
- **[Docker Docs](https://docs.docker.com/)** - Documentação oficial do Docker

### Ferramentas Recomendadas

- **VS Code** com extensões Python e Docker
- **Postman** para testar APIs
- **MySQL Workbench** para gerenciar banco
- **Git** para controle de versão

### Comandos Úteis

```bash
# Git
git status
git log --oneline
git diff

# Docker
docker ps
docker logs [container_id]
docker exec -it [container_id] bash

# Python
python -m pip list
python -m pip freeze > requirements.txt
python -c "import sys; print(sys.path)"
```

### Troubleshooting Rápido

```bash
# Verificar se o servidor está rodando
curl http://localhost:8001/health

# Verificar logs do Docker
docker-compose logs -f backend

# Verificar conexão com banco
python check_mysql.py

# Executar testes
python -m pytest tests/
```

### Próximos Passos

1. **Configure seu ambiente** seguindo o [Início Rápido](QUICK_START.md)
2. **Leia a [documentação técnica](backend/README.md)** do backend
3. **Explore os [exemplos de código](DEVELOPER_GUIDE.md)** neste guia
4. **Execute os testes** para verificar se tudo está funcionando
5. **Comece a desenvolver** sua primeira feature

### Recursos Adicionais

- **[Resumo da Documentação](DOCUMENTATION_SUMMARY.md)** - Índice completo de toda a documentação
- **[Guia Docker](DOCKER_GUIDE.md)** - Para problemas específicos do Docker
- **[Início Rápido](QUICK_START.md)** - Para configuração inicial
- **[Backend README](backend/README.md)** - Documentação técnica específica

### Documentação Externa

- **[FastAPI Docs](https://fastapi.tiangolo.com/)** - Documentação oficial do FastAPI
- **[SQLAlchemy Docs](https://docs.sqlalchemy.org/)** - Documentação oficial do SQLAlchemy
- **[Pydantic Docs](https://pydantic-docs.helpmanual.io/)** - Documentação oficial do Pydantic
- **[Docker Docs](https://docs.docker.com/)** - Documentação oficial do Docker

---

**Bem-vindo ao time de desenvolvimento! 🚀**
