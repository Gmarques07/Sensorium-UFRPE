# 🧪 Guia de Uso dos Scripts de Teste

Este documento explica como usar os scripts de teste disponíveis na pasta `scripts/`.

## 📋 Scripts Disponíveis

### 1. Scripts Interativos
- `run_tests.sh` - Script interativo para Linux/macOS
- `run_tests.bat` - Script interativo para Windows (CMD)
- `run_tests.ps1` - Script interativo para Windows (PowerShell)

### 2. Scripts de Linha de Comando
- `test.sh` - Script de comandos diretos para Linux/macOS

## 🐧 Linux/macOS

### Usando o script interativo:
```bash
cd backend/scripts
./run_tests.sh
```

### Usando comandos diretos:
```bash
cd backend/scripts
./test.sh all         # Executar todos os testes
./test.sh unit        # Apenas testes de unidade
./test.sh integration # Apenas testes de integração
./test.sh coverage    # Testes com cobertura
./test.sh clean       # Limpar containers de teste
./test.sh build       # Construir containers de teste
./test.sh help        # Mostrar ajuda
```

## 🪟 Windows

### Usando PowerShell:
```powershell
cd backend\scripts
.\run_tests.ps1
```

### Usando Command Prompt (CMD):
```cmd
cd backend\scripts
run_tests.bat
```

## 🎛️ Opções Disponíveis nos Scripts Interativos

1. **Executar todos os testes** - Roda testes de unidade e integração
2. **Executar testes de unidade** - Apenas testes que não requerem serviços externos
3. **Executar testes de integração** - Testes que requerem MySQL e backend em execução
4. **Executar testes com cobertura** - Mostra cobertura de código dos testes
5. **Executar testes específicos** - Permite executar arquivos ou testes específicos
6. **Limpar containers de teste** - Remove containers e volumes de teste
7. **Build dos containers de teste** - Reconstrói as imagens Docker
8. **Sair** - Encerra o script

## ⚠️ Importante sobre Testes de Integração

Os testes de integração **requerem** vários containers para funcionar:
- `sensorium_mysql` - Banco de dados MySQL (porta 3307)
- `sensorium_backend_int` - Backend para testes de integração (porta 8003)
- `sensorium_tests_integration` - Container executor dos testes

O serviço `backend_int` depende do MySQL para funcionar e é automaticamente iniciado quando você roda os testes de integração.

## ▶️ Iniciar o Container Principal da Aplicação (Porta 8001)

Para iniciar o container principal da aplicação (que roda na porta 8001):

```bash
# Iniciar o container principal
docker-compose up -d backend

# A aplicação estará disponível em: http://localhost:8001

# Verificar se está rodando
docker-compose ps

# Ver logs
docker-compose logs backend

# Parar o container
docker-compose stop backend

# Parar e remover o container
docker-compose down backend
```

**Importante**: Este container (`sensorium_backend` na porta 8001) é o backend principal da aplicação e não está relacionado diretamente aos testes. Ele usa o MySQL local do WAMP/XAMPP na porta 3306, diferente dos testes que usam o MySQL container na porta 3307.

## 🧹 Limpeza de Testes

Após executar os testes, especialmente os de integração, é recomendável limpar os containers:

```bash
# Linux/macOS
./test.sh clean

# Windows (qualquer script interativo)
# Escolher opção 6 no menu
```

## 🔧 Comandos Docker Diretos

Se preferir usar comandos Docker diretamente:

```bash
# Executar testes de unidade
docker-compose run --rm tests

# Executar testes de integração
docker-compose run --rm tests_integration

# Executar testes com cobertura
docker-compose run --rm tests pytest --cov=app --cov-report=term-missing

# Limpar tudo (importante!)
docker-compose down -v --remove-orphans

# Construir containers
docker-compose build tests tests_integration backend_int
```

## ⚠️ Problemas Comuns e Soluções

### 1. Container de integração não inicia:
```bash
# Reconstruir containers
./test.sh build

# Verificar logs
docker-compose logs backend_int
```

### 2. Conflito de nomes de containers:
```bash
# Limpar completamente
./test.sh clean
# Ou manualmente:
docker-compose down -v --remove-orphans
docker rm -f sensorium_mysql sensorium_backend sensorium_backend_int sensorium_tests sensorium_tests_integration 2>/dev/null || true
```

### 3. Testes falhando por dependências:
```bash
# Limpar e reconstruir
./test.sh clean
./test.sh build
```

### 4. Erros de permissão (Linux/macOS):
```bash
chmod +x *.sh
```

## 📚 Documentação Adicional

- [docs/TESTS_GUIDE.md](../docs/guides/TESTS_GUIDE.md) - Guia completo de testes