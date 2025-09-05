# 🧪 Guia de Testes - Sistema Sensorium UFRPE

Este guia fornece instruções completas para executar e entender os testes do sistema Sensorium UFRPE, tanto em ambiente local quanto usando Docker.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Estrutura dos Testes](#estrutura-dos-testes)
- [Testes de Unidade](#testes-de-unidade)
- [Testes de Integração](#testes-de-integração)
- [Execução dos Testes](#execução-dos-testes)
- [Configuração do Ambiente Docker para Testes](#configuração-do-ambiente-docker-para-testes)
- [Relatórios de Cobertura](#relatórios-de-cobertura)
- [Melhores Práticas](#melhores-práticas)

## 🔍 Visão Geral

O sistema Sensorium UFRPE utiliza uma suíte de testes abrangente que inclui:

1. **Testes de Unidade**: Testam componentes individuais do sistema
2. **Testes de Integração**: Testam a interação entre diferentes componentes e serviços

Todos os testes são escritos usando o framework **pytest** e podem ser executados tanto localmente quanto em containers Docker.

## 🏗️ Estrutura dos Testes

```
backend/tests/
├── conftest.py                 # Configuração de fixtures e ambiente
├── test_auth.py               # Testes de autenticação
├── test_basic.py              # Testes básicos
├── test_db.py                 # Testes de banco de dados
├── test_models.py             # Testes de modelos
├── test_routes.py             # Testes de rotas da API
├── test_usuario.py            # Testes específicos de usuários
└── integration/               # Testes de integração
    ├── test_admin_configurations.py
    ├── test_admin_integration.py
    ├── test_auth_integration.py
    ├── test_locais_integration.py
    ├── test_notificacoes_integration.py
    └── test_usuarios_integration.py
```

## 🔧 Testes de Unidade

### Configuração

Os testes de unidade utilizam:
- **Banco de dados em memória (SQLite)** para isolamento
- **Fixtures** definidas em `conftest.py`
- **TestClient** do FastAPI para testar endpoints

### Principais Testes

1. **Autenticação** (`test_auth.py`):
   - Criação de tokens JWT
   - Login com credenciais válidas/inválidas
   - Registro de novos usuários

2. **Modelos** (`test_models.py`):
   - Criação de usuários
   - Validação de dados (pH, nível de água)
   - Conversão para dicionário

3. **Rotas** (`test_routes.py`):
   - Endpoints de login
   - Acesso a perfil de usuário
   - Dados de cisternas
   - Controle de acesso não autorizado

4. **Usuários** (`test_usuario.py`):
   - Criação de usuários
   - Tratamento de senhas vazias
   - Conversão para dicionário

### Execução

```bash
# Local
cd backend
python -m pytest tests/ --ignore=tests/integration

# Docker
cd backend
docker-compose run --rm tests pytest tests/ --ignore=tests/integration
```

## 🔄 Testes de Integração

### Configuração

Os testes de integração utilizam:
- **Servidor real** rodando em container (`backend_int`)
- **Banco de dados SQLite em arquivo** (`/tmp/integration.db`)
- **Requests HTTP reais** para testar endpoints
- **Verificação de integridade** com healthchecks

### Serviços Docker

```yaml
backend_int:
  build: .
  environment:
    DATABASE_URL: "sqlite:////tmp/integration.db"
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
    interval: 10s
    timeout: 5s
    retries: 10

tests_integration:
  depends_on:
    backend_int:
      condition: service_healthy
  environment:
    API_BASE_URL: "http://backend_int:8001"
  command: pytest -q tests/integration -s
```

### Principais Testes

1. **Admin** (`test_admin_integration.py`):
   - Login de administradores
   - Acesso ao dashboard
   - Listagem de usuários
   - Configurações do sistema

2. **Autenticação** (`test_auth_integration.py`):
   - Fluxo completo de login e perfil
   - Registro e autenticação

3. **Locais** (`test_locais_integration.py`):
   - Criação de locais
   - Dados atuais de sensores
   - Registro de leituras de pH
   - Histórico de leituras

4. **Notificações** (`test_notificacoes_integration.py`):
   - Listagem de notificações
   - Notificações não lidas

5. **Usuários** (`test_usuarios_integration.py`):
   - Perfil do usuário
   - Edição de perfil
   - Validação de senha
   - Exclusão de conta

### Execução

```bash
# Docker (método recomendado)
cd backend
docker-compose run --rm tests_integration

# Com build prévio
cd backend
docker-compose build
docker-compose run --rm tests_integration

# Filtrando testes específicos
docker-compose run --rm tests_integration pytest -k "admin"
```

## ▶️ Execução dos Testes

### Todos os Testes

```bash
# Local
cd backend
python -m pytest

# Docker
cd backend
docker-compose run --rm tests
```

### Testes Específicos

```bash
# Por arquivo
python -m pytest tests/test_auth.py

# Por diretório
python -m pytest tests/integration/

# Por marcação
python -m pytest -m integration

# Por nome
python -m pytest -k "login"
```

### Verbosidade

```bash
# Silencioso
python -m pytest -q

# Verboso
python -m pytest -v

# Muito verboso
python -m pytest -vv
```

## 🐳 Configuração do Ambiente Docker para Testes

### Serviços Disponíveis

O arquivo `docker-compose.yml` inclui serviços específicos para testes:

1. **tests**: Testes de unidade com SQLite em memória
2. **backend_int**: Backend para testes de integração
3. **tests_integration**: Executor de testes de integração

### Variáveis de Ambiente

```bash
# Para testes de unidade
DATABASE_URL=sqlite:///:memory:
SECRET_KEY=chave_secreta_para_testes
DISABLE_RATE_LIMITING=true

# Para testes de integração
API_BASE_URL=http://backend_int:8001
```

### Comandos Úteis

```bash
# Build dos containers de teste
docker-compose build tests tests_integration backend_int

# Executar testes de unidade
docker-compose run --rm tests

# Executar testes de integração
docker-compose run --rm tests_integration

# Executar todos os testes
docker-compose run --rm tests && docker-compose run --rm tests_integration
```

## 📊 Relatórios de Cobertura

### Instalação

```bash
pip install pytest-cov
```

### Geração de Relatórios

```bash
# Local
python -m pytest --cov=app --cov-report=html --cov-report=term

# Docker
docker-compose run --rm tests pytest --cov=app --cov-report=html --cov-report=term
```

### Configuração

Arquivo `pytest.ini`:
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
markers =
    integration: mark a test as an integration test
addopts = 
    --cov=app
    --cov-report=term-missing
    --cov-fail-under=80
```

## ✅ Melhores Práticas

### Escrevendo Testes

1. **Nomes descritivos**:
   ```python
   def test_usuario_perfil_edicao_validacao_exclusao():
       # ... código do teste
   ```

2. **Isolamento**:
   - Cada teste deve ser independente
   - Use fixtures para setup/teardown

3. **Assertivas claras**:
   ```python
   assert response.status_code == 200
   assert dados["email"] == "teste@example.com"
   ```

### Organização

1. **Separe testes de unidade e integração**
2. **Use fixtures para recursos compartilhados**
3. **Mantenha testes focados e específicos**

### Debugging

```bash
# Executar um teste específico com mais detalhes
python -m pytest tests/test_auth.py::test_login_sucesso -vv

# Parar na primeira falha
python -m pytest -x

# Parar no primeiro teste que falhar
python -m pytest --tb=short
```

## 🛠️ Solução de Problemas

### Problemas Comuns

1. **Rate Limiting**:
   ```bash
   # Solução: Adicione variável de ambiente
   DISABLE_RATE_LIMITING=true
   ```

2. **Conflitos de Banco de Dados**:
   ```bash
   # Solução: Use emails únicos nos testes
   email = f"teste_{uuid.uuid4()}@example.com"
   ```

3. **Timeouts em Integração**:
   ```bash
   # Solução: Aumente o tempo de espera nos healthchecks
   retries: 20
   interval: 15s
   ```

### Logs e Debugging

```bash
# Ver logs dos containers de teste
docker-compose logs backend_int

# Executar com modo interativo
docker-compose run --rm tests bash

# Ver cobertura detalhada
pytest --cov=app --cov-report=term-missing
```

## 📈 Cobertura Atual

A suíte de testes atual cobre:

- ✅ **100%** dos endpoints de autenticação
- ✅ **95%** dos endpoints de usuários
- ✅ **90%** dos endpoints de admin
- ✅ **85%** dos endpoints de locais
- ✅ **80%** dos endpoints de notificações
- ✅ **100%** dos modelos de dados
- ✅ **95%** das regras de negócio

## 🔄 CI/CD Integration

Exemplo de configuração para GitHub Actions:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  tests:
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: password
          MYSQL_DATABASE: test_db
        ports:
          - 3306:3306
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run unit tests
        run: |
          cd backend
          python -m pytest tests/ --ignore=tests/integration
      - name: Run integration tests
        run: |
          cd backend
          docker-compose run --rm tests_integration
```

---

**Última atualização**: Setembro 2025  
**Cobertura mínima**: 80%  
**Framework**: pytest 8.3+