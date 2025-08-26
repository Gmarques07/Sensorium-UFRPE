# Guia de Instalação - Sensorium UFRPE Backend

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git

## 🚀 Instalação Passo a Passo

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/Sensorium-UFRPE.git
cd Sensorium-UFRPE/backend
```

### 2. Crie um ambiente virtual (RECOMENDADO)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure o arquivo .env
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env com suas configurações
```

### 5. Configurações do Banco de Dados

#### Opção A: Banco Local (MySQL)
```env
MYSQL_USER=root
MYSQL_PASSWORD=sua_senha
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=sensorium_db
```

#### Opção B: Railway (Recomendado)
```env
MYSQL_USER=root
MYSQL_PASSWORD=osOvMtonkwxcbEphriXeJGPKdOxSfAzl
MYSQL_HOST=ballast.proxy.rlwy.net
MYSQL_PORT=56724
MYSQL_DATABASE=railway
```

### 6. Configure a chave secreta
```env
# Gere uma chave secreta segura (mínimo 32 caracteres)
SECRET_KEY=sua_chave_secreta_muito_longa_e_segura_para_jwt_tokens_aqui
```

### 7. Teste a conexão com o banco
```bash
python test_db_connection.py
```

### 8. Inicie o servidor
```bash
# Desenvolvimento
python start_server.py --reload

# Produção
python start_server.py
```

## 🔧 Solução de Problemas Comuns

### Erro: "No module named 'sqlalchemy'"
```bash
pip install -r requirements.txt
```

### Erro: "Authentication plugin 'caching_sha2_password' is not supported"
- ✅ Já resolvido no requirements.txt atualizado
- Se persistir: `pip install --upgrade mysql-connector-python`

### Erro: "Can't connect to MySQL server"
- Verifique se as credenciais no `.env` estão corretas
- Teste a conexão: `python test_db_connection.py`

### Erro: "ModuleNotFoundError: No module named 'pydantic_settings'"
```bash
pip install pydantic-settings
```

## 📁 Estrutura do Projeto

```
backend/
├── app/
│   ├── api/           # Endpoints da API
│   ├── core/          # Configurações
│   ├── crud/          # Operações do banco
│   ├── db/            # Configuração do banco
│   ├── models/        # Modelos SQLAlchemy
│   └── schemas/       # Schemas Pydantic
├── templates/         # Templates HTML
├── static/           # Arquivos estáticos
├── requirements.txt  # Dependências
├── .env             # Configurações (criar)
└── start_server.py  # Script de inicialização
```

## 🌐 URLs Importantes

- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Frontend**: http://localhost:8000

## 🔐 Credenciais Padrão

### Admin
- **Email**: admin@sensorium.com
- **Senha**: admin123

### Usuário Teste
- **CPF**: 12345678900
- **Senha**: teste123

## 📞 Suporte

Se encontrar problemas:
1. Verifique se todas as dependências foram instaladas
2. Confirme se o arquivo `.env` está configurado corretamente
3. Teste a conexão com o banco de dados
4. Verifique os logs do servidor

## 🚀 Deploy

Para produção, considere:
- Usar um servidor WSGI como Gunicorn
- Configurar um proxy reverso (Nginx)
- Usar variáveis de ambiente para configurações sensíveis
- Configurar SSL/HTTPS
