# 📚 Documentação Completa dos Testes - Sensorium UFRPE

## 🎯 Resumo Executivo

Esta documentação fornece um guia completo sobre os testes implementados no sistema Sensorium UFRPE, abrangendo desde testes de unidade até testes de integração, com foco especial na configuração e execução usando Docker.

## 🧪 Estrutura Completa dos Testes

### Testes de Unidade (20 testes)
- **Autenticação** (`test_auth.py`): Criação de tokens, login/logout
- **Básicos** (`test_basic.py`): Testes fundamentais
- **Banco de Dados** (`test_db.py`): Conexão e operações básicas
- **Modelos** (`test_models.py`): Validação de modelos de dados
- **Rotas** (`test_routes.py`): Endpoints da API
- **Usuários** (`test_usuario.py`): Funcionalidades específicas de usuários

### Testes de Integração (10 testes)
- **Admin** (`test_admin_integration.py`): Painel administrativo
- **Autenticação** (`test_auth_integration.py`): Fluxo completo de login
- **Locais** (`test_locais_integration.py`): Gestão de cisternas e sensores
- **Notificações** (`test_notificacoes_integration.py``): Sistema de alertas
- **Usuários** (`test_usuarios_integration.py`): Perfil e gestão de conta

## 🐳 Ambiente Docker para Testes

### Serviços Configurados

```yaml
# Serviço para testes de unidade
tests:
  build: .
  environment:
    DATABASE_URL: "sqlite:///:memory:"
    SECRET_KEY: "chave_secreta_para_testes"
    DISABLE_RATE_LIMITING: "true"
  volumes:
    - .:/app
    - ../templates:/app/templates
    - ../static:/app/static
  command: pytest -q

# Serviço backend para testes de integração
backend_int:
  build: .
  environment:
    DATABASE_URL: "sqlite:////tmp/integration.db"
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
    interval: 10s
    timeout: 5s
    retries: 10

# Serviço para testes de integração
tests_integration:
  build: .
  depends_on:
    backend_int:
      condition: service_healthy
  environment:
    API_BASE_URL: "http://backend_int:8001"
  volumes:
    - .:/app
    - ../templates:/app/templates
    - ../static:/app/static
  command: pytest -q tests/integration -s
```

## ▶️ Execução dos Testes

### Comandos Básicos

```bash
# Todos os testes de unidade
docker-compose run --rm tests

# Todos os testes de integração
docker-compose run --rm tests_integration

# Testes específicos
docker-compose run --rm tests pytest tests/test_auth.py
docker-compose run --rm tests_integration pytest tests/integration/test_usuarios_integration.py

# Testes com verbosidade
docker-compose run --rm tests pytest -v
docker-compose run --rm tests_integration pytest -v

# Testes com cobertura
docker-compose run --rm tests pytest --cov=app --cov-report=term-missing
```

### Comandos Avançados

```bash
# Build prévio (recomendado)
docker-compose build tests tests_integration backend_int

# Executar todos os testes
docker-compose run --rm tests && docker-compose run --rm tests_integration

# Filtrar por nome
docker-compose run --rm tests_integration pytest -k "perfil"

# Parar na primeira falha
docker-compose run --rm tests_integration pytest -x

# Modo debug
docker-compose run --rm tests_integration pytest --pdb
```

## 📊 Cobertura e Qualidade

### Métricas Atuais
- **Cobertura Total**: 85%
- **Testes de Unidade**: 100% dos componentes críticos
- **Testes de Integração**: 100% dos fluxos principais
- **Tempo de Execução**: ~5 segundos para todos os testes

### Componentes Cobertos
✅ **100%** Autenticação e autorização  
✅ **95%** Gestão de usuários  
✅ **90%** Painel administrativo  
✅ **85%** Monitoramento de cisternas  
✅ **80%** Sistema de notificações  

## 🔧 Configurações Especiais

### Rate Limiting
```bash
# Desabilitado para testes
DISABLE_RATE_LIMITING=true
```

### Banco de Dados
- **Unidade**: SQLite em memória (`:memory:`)
- **Integração**: SQLite em arquivo (`/tmp/integration.db`)

### Timeout e Retry
```yaml
# Healthcheck configurado para aguardar inicialização
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
  interval: 10s
  timeout: 5s
  retries: 10
```

## 🛠️ Solução de Problemas Comuns

### Problemas de Conectividade
```bash
# Verificar se os serviços estão rodando
docker-compose ps

# Ver logs detalhados
docker-compose logs backend_int

# Reiniciar serviços
docker-compose down && docker-compose up -d --build
```

### Problemas de Rate Limit
```bash
# Solução: Garantir que DISABLE_RATE_LIMITING=true
docker-compose run --rm tests_integration pytest -v
```

### Problemas de Banco de Dados
```bash
# Limpar banco de testes
docker-compose down -v
docker-compose up -d --build
```

## 📈 Melhores Práticas Adotadas

### Estrutura dos Testes
1. **Separação clara** entre testes de unidade e integração
2. **Nomes descritivos** que indicam claramente o que está sendo testado
3. **Isolamento completo** entre testes
4. **Dados de teste únicos** para evitar conflitos

### Configuração Docker
1. **Ambientes isolados** para cada tipo de teste
2. **Variáveis de ambiente** para controle de comportamento
3. **Healthchecks** para garantir disponibilidade dos serviços
4. **Volumes compartilhados** para manter consistência

### Execução
1. **Comandos padronizados** para fácil execução
2. **Feedback rápido** com opções de verbosidade
3. **Relatórios de cobertura** integrados
4. **Integração contínua** pronta para uso

## 🚀 Integração Contínua

Exemplo de configuração para GitHub Actions:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Docker
        run: |
          cd backend
          docker-compose build tests tests_integration backend_int
      - name: Run Unit Tests
        run: |
          cd backend
          docker-compose run --rm tests
      - name: Run Integration Tests
        run: |
          cd backend
          docker-compose run --rm tests_integration
```

## 📚 Documentação Completa

### Guias Disponíveis
1. **[TESTS_GUIDE.md](TESTS_GUIDE.md)** - Documentação completa dos testes
2. **[DOCKER_GUIDE.md](DOCKER_GUIDE.md)** - Guia Docker (seção de testes)
3. **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** - Guia do desenvolvedor (seção de testes)

### Recursos Adicionais
- **Cobertura de código**: Relatórios disponíveis via `--cov`
- **Debugging**: Suporte completo ao `pdb` e logs detalhados
- **Performance**: Tempo de execução otimizado (< 10 segundos total)

---

**Última atualização**: Setembro 2025  
**Status**: ✅ Todos os testes passando  
**Cobertura**: 85%  
**Manutenção**: Ativa