# Documentação da Migração: Flask para FastAPI

## Visão Geral
Este documento detalha o processo de migração do projeto Sensorium-UFRPE de Flask para FastAPI, incluindo as mudanças na estrutura do projeto, endpoints migrados e melhorias implementadas.

## Estrutura do Projeto
### Antes (Flask)
```
/
├── app.py              # Arquivo principal com todas as rotas
├── static/            
└── templates/          # Templates HTML
```

### Depois (FastAPI)
```
/backend
├── app/
│   ├── api/
│   │   ├── deps.py
│   │   └── endpoints/    # Rotas da API organizadas por recurso
│   ├── core/            # Configurações e segurança
│   ├── crud/            # Operações do banco de dados
│   ├── models/          # Modelos SQLAlchemy
│   └── schemas/         # Schemas Pydantic
└── main.py             # Arquivo principal da aplicação FastAPI
```

## Componentes Migrados

### 1. Autenticação
- Migrado de Flask-Login para JWT com python-jose
- Implementado sistema de tokens JWT para autenticação
- Adicionada validação de senha com passlib[bcrypt]

### 2. Modelos de Dados
- Convertidos modelos Flask-SQLAlchemy para SQLAlchemy puro
- Implementados Pydantic schemas para validação de dados
- Separação clara entre modelos de banco de dados e schemas de API

### 3. Endpoints Migrados
#### Usuários
- POST /usuarios/registro
- POST /usuarios/login
- GET /usuarios/me
- PUT /usuarios/{id}

#### Administrador
- POST /admin/login
- GET /admin/usuarios
- PUT /admin/usuarios/{id}

#### Cisternas
- GET /cisternas
- POST /cisternas
- PUT /cisternas/{id}
- DELETE /cisternas/{id}

#### Notificações
- GET /notificacoes
- POST /notificacoes
- PUT /notificacoes/{id}
- DELETE /notificacoes/{id}

### 4. Sistema de Dependências
- Implementado sistema de injeção de dependências
- Criado gerenciamento de sessões do banco de dados
- Adicionada validação de usuário atual

## Melhorias Implementadas

### Performance
- Lazy loading de relacionamentos
- Queries otimizadas com joins apropriados
- Paginação implementada em listagens

### Segurança
- Tokens JWT com expiração
- Senhas hasheadas com bcrypt
- Validação de dados com Pydantic

### Manutenibilidade
- Código organizado por recursos
- Separação clara de responsabilidades
- Documentação automática com OpenAPI/Swagger

## Dependências Atualizadas
```
# API e Framework
fastapi==0.103.1
uvicorn==0.23.2

# Banco de Dados
sqlalchemy==2.0.20
mysql-connector-python==8.1.0
alembic==1.12.0

# Validação e Serialização
pydantic==2.3.0
pydantic-settings==2.0.3
email-validator==2.0.0

# Autenticação e Segurança
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
```

## Estado Atual
- ✅ Autenticação migrada
- ✅ CRUD de usuários migrado
- ✅ CRUD de cisternas migrado
- ✅ Sistema de notificações migrado
- ✅ Painel administrativo migrado
- ⏳ Interface web ainda em Flask (em processo de migração)

## Próximos Passos
1. Migrar completamente a interface web para um framework frontend moderno
2. Implementar testes automatizados para todos os endpoints
3. Adicionar documentação detalhada com exemplos
4. Configurar CI/CD com GitHub Actions
5. Implementar monitoramento e logging

## Notas de Desenvolvimento
- Manter compatibilidade temporária com Flask durante a migração
- Usar branches separados para cada componente migrado
- Testes devem ser escritos antes da migração de cada componente
- Documentar todas as mudanças breaking changes

## Comandos Úteis
```bash
# Rodar o servidor FastAPI
uvicorn backend.main:app --reload

# Executar testes
pytest

# Formatar código
black .
flake8
isort .

# Gerar documentação
mkdocs serve
```

## Documentação Adicional
- Documentação FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy 2.0: https://docs.sqlalchemy.org/en/20/
- Pydantic v2: https://docs.pydantic.dev/latest/
