# 🚀 Início Rápido - Sistema Sensorium UFRPE

Este guia permite que você escolha entre duas formas de executar o sistema: **Docker** (mais fácil) ou **Local** (mais flexível).

## 🎯 Escolha Sua Opção

### 🐳 Opção 1: Docker (Recomendado para iniciantes)

**Vantagens:**
- ✅ Instalação mais simples
- ✅ Não precisa configurar Python/MySQL
- ✅ Ambiente isolado
- ✅ Funciona em qualquer sistema operacional

**Pré-requisitos:**
- Docker Desktop instalado
- MySQL local (WAMP/XAMPP/LAMP) rodando

**Passos:**
```bash
# 1. Clone o repositório
git clone [URL_DO_REPOSITORIO]
cd Sensorium-UFRPE

# 2. Execute com Docker
cd backend
docker-compose up -d --build

# 3. Acesse o sistema
# Frontend: http://localhost:8001
# API Docs: http://localhost:8001/docs
```

### 🖥️ Opção 2: Instalação Local

**Vantagens:**
- ✅ Melhor para desenvolvimento
- ✅ Debugging mais fácil
- ✅ Performance nativa
- ✅ Controle total do ambiente

**Pré-requisitos:**
- Python 3.7+
- MySQL Server
- pip

**Passos:**
```bash
# 1. Clone o repositório
git clone [URL_DO_REPOSITORIO]
cd Sensorium-UFRPE/backend

# 2. Configure o ambiente
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure o banco
cp env.example .env
# Edite o arquivo .env com suas configurações

# 5. Inicialize o banco
python init_db.py

# 6. Inicie o servidor
python start_server.py --reload

# 7. Acesse o sistema
# Frontend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## 🔧 Configuração do MySQL

### Para Docker
O sistema está configurado para usar seu MySQL local automaticamente.

### Para Instalação Local
1. **Instale o MySQL Server**
2. **Crie o banco de dados:**
```sql
CREATE DATABASE banco_de_dados;
```
3. **Configure o arquivo .env:**
```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=sua_senha
MYSQL_DATABASE=banco_de_dados
MYSQL_PORT=3306
```

## 🎮 Comandos Úteis

### Docker
```bash
# Iniciar
docker-compose up -d

# Parar
docker-compose down

# Ver logs
docker-compose logs -f backend

# Rebuild
docker-compose up -d --build
```

### Local
```bash
# Iniciar com reload
python start_server.py --reload

# Iniciar em produção
python start_server.py

# Verificar conexão MySQL
python check_mysql.py

# Inicializar banco
python init_db.py
```

## 🌐 Acessos

| Ambiente | Frontend | API Docs | Health Check |
|----------|----------|----------|--------------|
| **Docker** | http://localhost:8001 | http://localhost:8001/docs | http://localhost:8001/health |
| **Local** | http://localhost:8000 | http://localhost:8000/docs | http://localhost:8000/health |

## 🆘 Solução de Problemas

### Docker
- **Container não inicia**: Verifique se o MySQL está rodando
- **Porta ocupada**: Pare outros serviços na porta 8001
- **Erro de permissão**: Verifique as permissões dos diretórios

### Local
- **Erro de dependências**: Execute `pip install -r requirements.txt`
- **Erro de banco**: Verifique as configurações no .env
- **Porta ocupada**: Pare outros serviços na porta 8000

## 📚 Documentação Completa

- **[Resumo da Documentação](DOCUMENTATION_SUMMARY.md)** - Índice completo de toda a documentação
- **[Guia Docker Completo](DOCKER_GUIDE.md)** - Instruções detalhadas para Docker
- **[Guia do Desenvolvedor](DEVELOPER_GUIDE.md)** - Informações técnicas para desenvolvedores
- **[README Principal](README.md)** - Visão geral do projeto
- **[Backend README](backend/README.md)** - Documentação técnica

## 🤝 Precisa de Ajuda?

1. **Consulte a documentação** completa
2. **Verifique os logs** do sistema
3. **Abra uma issue** no repositório
4. **Entre em contato** com a equipe

---

**Escolha sua opção e comece a usar o sistema! 🚀**
