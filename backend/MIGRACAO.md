# Migração Flask para FastAPI - Documentação

## 1. Estrutura do Projeto

A nova estrutura do projeto foi organizada da seguinte forma:

```
sensorium-ufrpe/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py         # Autenticação e registro
│   │   │   │   └── cisterna.py     # Endpoints da cisterna
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py               # Configurações do projeto
│   │   └── security.py             # Funções de segurança
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py             # Configuração do banco de dados
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py               # Modelos SQLAlchemy
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schemas.py              # Schemas Pydantic
│   └── __init__.py
├── main.py                         # Arquivo principal
└── requirements.txt                # Dependências do projeto
```

## 2. Principais Alterações

### 2.1 Mudanças na Arquitetura
- Migração do Flask para FastAPI
- Substituição do Flask-SQLAlchemy por SQLAlchemy puro
- Implementação de schemas Pydantic para validação de dados
- Remoção de templates (separação clara entre frontend e backend)

### 2.2 Autenticação
- Implementação de JWT (JSON Web Tokens)
- Rota de login usando OAuth2PasswordBearer
- Rota de registro com validação de dados
- Funções de hash de senha mais seguras

### 2.3 Modelos de Dados
Foram mantidos os seguintes modelos, agora usando SQLAlchemy:
- Usuario
- PhNivel
- NivelAgua

### 2.4 Endpoints da API

#### Autenticação (/api/v1)
- POST /login
  - Login de usuário usando CPF e senha
  - Retorna token JWT
- POST /signup
  - Registro de novo usuário
  - Validação automática de dados

#### Cisterna (/api/v1/cisterna)
- GET /dados-atuais/{dispositivo_id}
  - Retorna dados atuais de pH e nível
- GET /historico/{dispositivo_id}
  - Retorna histórico de leituras
- GET /nivel-agua/{dispositivo_id}
  - Retorna nível atual da água

## 3. Novas Dependências

```
fastapi==0.103.1
uvicorn==0.23.2
sqlalchemy==2.0.20
pydantic==2.3.0
pydantic-settings==2.0.3
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
mysql-connector-python==8.1.0
email-validator==2.0.0
```

## 4. Melhorias Implementadas

1. **Documentação Automática**
   - Swagger UI (/docs)
   - ReDoc (/redoc)

2. **Validação de Dados**
   - Validação automática com Pydantic
   - Tipagem forte em todos os endpoints
   - Melhor tratamento de erros

3. **Segurança**
   - Autenticação JWT
   - Hash de senhas com bcrypt
   - Middleware CORS configurável

4. **Performance**
   - Suporte a operações assíncronas
   - Conexões eficientes com banco de dados
   - Melhor gerenciamento de recursos

## 5. Como Executar

1. Instalar dependências:
```bash
pip install -r requirements.txt
```

2. Configurar variáveis em app/core/config.py:
```python
MYSQL_USER = "seu_usuario"
MYSQL_PASSWORD = "sua_senha"
MYSQL_HOST = "localhost"
MYSQL_DATABASE = "banco_de_dados"
```

3. Executar o servidor:
```bash
uvicorn main:app --reload
```

4. Acessar a documentação:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 6. Próximos Passos

1. **Implementar mais endpoints**
   - Endpoints para administração
   - Endpoints para notificações
   - Endpoints para configurações do sistema

2. **Melhorias de segurança**
   - Implementar rate limiting
   - Adicionar mais camadas de autenticação
   - Melhorar validação de dados

3. **Documentação**
   - Adicionar exemplos de uso
   - Documentar todos os endpoints
   - Criar guias de desenvolvimento

4. **Testes**
   - Implementar testes unitários
   - Implementar testes de integração
   - Configurar CI/CD
