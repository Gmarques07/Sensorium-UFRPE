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
3. **Executar testes de integração** - Testes que requerem o serviço backend em execução
4. **Executar testes com cobertura** - Mostra cobertura de código dos testes
5. **Executar testes específicos** - Permite executar arquivos ou testes específicos
6. **Limpar containers de teste** - Remove containers e volumes de teste
7. **Build dos containers de teste** - Reconstrói as imagens Docker
8. **Sair** - Encerra o script

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
docker-compose -f config/docker-compose.yml run --rm tests

# Executar testes de integração
docker-compose -f config/docker-compose.yml run --rm tests_integration

# Executar testes com cobertura
docker-compose -f config/docker-compose.yml run --rm tests pytest --cov=app --cov-report=term-missing

# Limpar tudo
docker-compose -f config/docker-compose.yml down -v

# Construir containers
docker-compose -f config/docker-compose.yml build tests tests_integration backend_int
```

## ⚠️ Problemas Comuns e Soluções

### 1. Container de integração não inicia:
```bash
# Reconstruir containers
./test.sh build

# Verificar logs
docker-compose -f config/docker-compose.yml logs backend_int
```

### 2. Testes falhando por dependências:
```bash
# Limpar e reconstruir
./test.sh clean
./test.sh build
```

### 3. Erros de permissão (Linux/macOS):
```bash
chmod +x *.sh
```

## 📚 Documentação Adicional

- [docs/TESTS_GUIDE.md](../docs/guides/TESTS_GUIDE.md) - Guia completo de testes
- [docs/TESTS_EXECUTIVE_SUMMARY.md](../docs/guides/TESTS_EXECUTIVE_SUMMARY.md) - Resumo executivo dos testes
- [docs/DEVELOPER_GUIDE.md](../docs/guides/DEVELOPER_GUIDE.md) - Guia do desenvolvedor