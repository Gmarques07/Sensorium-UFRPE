# 🐳 Guia Docker - Sistema Sensorium UFRPE

Este guia fornece instruções completas para executar o sistema Sensorium UFRPE usando Docker, permitindo que os participantes do projeto escolham entre executar localmente ou via containers.

## 📋 Índice

- [Pré-requisitos](#pré-requisitos)
- [Instalação Rápida](#instalação-rápida)
- [Configuração Detalhada](#configuração-detalhada)
- [Comandos Úteis](#comandos-úteis)
- [Solução de Problemas](#solução-de-problemas)
- [Comparação: Docker vs Local](#comparação-docker-vs-local)

## 🔧 Pré-requisitos

### Obrigatórios
- **Docker Desktop** (Windows/Mac) ou **Docker Engine** (Linux)
- **Docker Compose** (incluído no Docker Desktop)
- **Git** (para clonar o repositório)

### Opcionais
- **MySQL Workbench** ou **phpMyAdmin** (para gerenciar o banco)
- **VS Code** com extensão Docker

## 🚀 Instalação Rápida

### 1. Clone o Repositório
```bash
git clone [URL_DO_REPOSITORIO]
cd Sensorium-UFRPE
```

### 2. Execute com Docker Compose
```bash
cd backend
docker-compose up -d --build
```

### 3. Acesse o Sistema
- **Frontend**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

## ⚙️ Configuração Detalhada

### Estrutura do Docker

```
backend/
├── Dockerfile              # Imagem do backend
├── docker-compose.yml      # Orquestração dos serviços
├── .dockerignore          # Arquivos ignorados no build
└── .env                   # Variáveis de ambiente
```

### Arquivo docker-compose.yml

O arquivo `docker-compose.yml` define os seguintes serviços:

```yaml
services:
  backend:
    build: .
    container_name: sensorium_backend
    restart: unless-stopped
    ports:
      - "8001:8001"
    volumes:
      - ../templates:/app/templates
      - ../static:/app/static
    environment:
      - MYSQL_HOST=host.docker.internal
      - MYSQL_USER=root
      - MYSQL_PASSWORD=
      - MYSQL_DATABASE=banco_de_dados
      - MYSQL_PORT=3306
      - SECRET_KEY=chave_secreta_muito_longa_e_segura_para_jwt_tokens_aqui
      - ACCESS_TOKEN_EXPIRE_MINUTES=1440
      - BACKEND_CORS_ORIGINS=["*"]
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=debug
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 5s
      retries: 3
```

### Configuração do Banco de Dados

O sistema está configurado para usar o MySQL local do seu sistema (WAMP/XAMPP/LAMP). 

**Configuração atual:**
- **Host**: `host.docker.internal` (acessa o MySQL local)
- **Porta**: `3306`
- **Usuário**: `root`
- **Senha**: (vazia - ajuste conforme necessário)
- **Banco**: `banco_de_dados`

### Personalizando a Configuração

1. **Edite o arquivo `.env`** (se existir):
```bash
# Configurações do MySQL
MYSQL_HOST=host.docker.internal
MYSQL_USER=root
MYSQL_PASSWORD=sua_senha_aqui
MYSQL_DATABASE=seu_banco_aqui
MYSQL_PORT=3306

# Configurações de Segurança
SECRET_KEY=sua_chave_secreta_muito_longa_e_segura
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Configurações de CORS
BACKEND_CORS_ORIGINS=["*"]
```

2. **Ou edite diretamente o docker-compose.yml**:
```yaml
environment:
  - MYSQL_PASSWORD=sua_senha_aqui
  - MYSQL_DATABASE=seu_banco_aqui
  - SECRET_KEY=sua_chave_secreta
```

## 🛠️ Comandos Úteis

### Gerenciamento de Containers

```bash
# Iniciar os serviços
docker-compose up -d

# Parar os serviços
docker-compose down

# Reiniciar os serviços
docker-compose restart

# Rebuild e iniciar
docker-compose up -d --build

# Ver logs em tempo real
docker-compose logs -f backend

# Ver status dos containers
docker-compose ps
```

### Desenvolvimento

```bash
# Executar comandos dentro do container
docker-compose exec backend bash

# Instalar dependências adicionais
docker-compose exec backend pip install nova_dependencia

# Executar scripts Python
docker-compose exec backend python init_db.py

# Verificar logs específicos
docker-compose logs backend | grep ERROR
```

### Manutenção

```bash
# Limpar containers parados
docker container prune

# Limpar imagens não utilizadas
docker image prune

# Limpar volumes não utilizados
docker volume prune

# Limpar tudo (cuidado!)
docker system prune -a
```

## 🔍 Solução de Problemas

### Problema: Container não inicia

**Sintomas:**
- Container para imediatamente após iniciar
- Erro de conexão com banco de dados

**Soluções:**
1. Verifique se o MySQL está rodando localmente
2. Confirme as credenciais no docker-compose.yml
3. Verifique os logs: `docker-compose logs backend`

### Problema: Erro de permissão

**Sintomas:**
- Erro ao acessar arquivos de templates/static
- Container não consegue escrever arquivos

**Soluções:**
1. Verifique as permissões dos diretórios:
```bash
chmod -R 755 templates/
chmod -R 755 static/
```

2. No Windows, certifique-se de que o Docker Desktop tem acesso aos drives

### Problema: Porta já em uso

**Sintomas:**
- Erro "port is already allocated"
- Container não consegue iniciar

**Soluções:**
1. Pare outros serviços na porta 8001:
```bash
# Windows
netstat -ano | findstr :8001
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8001 | xargs kill -9
```

2. Ou altere a porta no docker-compose.yml:
```yaml
ports:
  - "8002:8001"  # Muda para porta 8002
```

### Problema: Dados não aparecem

**Sintomas:**
- Dashboard vazio
- Sensores não carregam

**Soluções:**
1. Verifique se o banco de dados tem dados:
```bash
docker-compose exec backend python init_db.py
```

2. Verifique os logs da API:
```bash
docker-compose logs backend | grep "dashboard-dados"
```

## 📊 Comparação: Docker vs Local

| Aspecto | Docker | Local (start_server.py) |
|---------|--------|-------------------------|
| **Instalação** | ✅ Simples (apenas Docker) | ⚠️ Requer Python + MySQL |
| **Configuração** | ✅ Isolada | ⚠️ Pode conflitar com outros projetos |
| **Dependências** | ✅ Gerenciadas automaticamente | ⚠️ Instalação manual |
| **Performance** | ⚠️ Ligeiramente menor | ✅ Nativa |
| **Debugging** | ⚠️ Requer ferramentas específicas | ✅ Ferramentas nativas |
| **Deploy** | ✅ Pronto para produção | ⚠️ Requer configuração adicional |
| **Compatibilidade** | ✅ Funciona em qualquer OS | ⚠️ Depende do ambiente |

## 🎯 Quando Usar Cada Opção

### Use Docker quando:
- ✅ Você é novo no projeto
- ✅ Quer evitar configuração de ambiente
- ✅ Está em uma máquina compartilhada
- ✅ Quer garantir consistência entre desenvolvedores
- ✅ Está preparando para deploy

### Use Local quando:
- ✅ Você está desenvolvendo ativamente
- ✅ Precisa de debugging avançado
- ✅ Tem configuração específica de ambiente
- ✅ Quer máxima performance
- ✅ Está fazendo testes extensivos

## 🔄 Migração entre Ambientes

### Do Local para Docker:
```bash
# 1. Pare o servidor local
# 2. Execute o Docker
cd backend
docker-compose up -d --build
```

### Do Docker para Local:
```bash
# 1. Pare o Docker
docker-compose down

# 2. Execute localmente
cd backend
python start_server.py --reload
```

## 📝 Notas Importantes

1. **Dados**: O Docker usa o mesmo banco de dados local, então os dados são compartilhados entre os ambientes.

2. **Templates**: Os templates são montados como volumes, então mudanças são refletidas imediatamente.

3. **Logs**: Use `docker-compose logs -f backend` para acompanhar os logs em tempo real.

4. **Desenvolvimento**: Para desenvolvimento ativo, considere usar o ambiente local para melhor debugging.

5. **Produção**: Para deploy em produção, use Docker com um banco de dados gerenciado.

## 🆘 Suporte

Se encontrar problemas:

1. **Verifique os logs**: `docker-compose logs backend`
2. **Consulte este guia**: Procure na seção de solução de problemas
3. **Resumo da Documentação**: [DOCUMENTATION_SUMMARY.md](DOCUMENTATION_SUMMARY.md) para encontrar informações específicas
4. **Guia do Desenvolvedor**: [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) para informações técnicas
5. **Abra uma issue**: No repositório do projeto
6. **Contate a equipe**: Para suporte específico

---

**Última atualização**: Janeiro 2024  
**Versão do Docker**: 20.10+  
**Versão do Docker Compose**: 2.0+
