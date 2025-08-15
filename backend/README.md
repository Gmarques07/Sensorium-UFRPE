# Backend Sensorium-UFRPE

Backend do projeto Sensorium-UFRPE desenvolvido com FastAPI.

## Tecnologias Utilizadas

- FastAPI
- SQLAlchemy
- Pydantic
- MySQL
- JWT para autenticação

## Configuração do Ambiente

1. Criar ambiente virtual:
```bash
python -m venv venv
```

2. Ativar ambiente virtual:
```bash
# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Instalar dependências:
```bash
pip install -r requirements.txt
```

4. Configurar variáveis de ambiente em `app/core/config.py`

5. Executar o servidor:
```bash
uvicorn main:app --reload
```

## Estrutura do Projeto

```
backend/
├── app/                    # Código principal
│   ├── api/               # Rotas da API
│   ├── core/              # Configurações
│   ├── db/                # Banco de dados
│   ├── models/            # Modelos SQLAlchemy
│   └── schemas/           # Schemas Pydantic
├── tests/                 # Testes
└── main.py               # Ponto de entrada
```

## Documentação da API

Com o servidor rodando, acesse:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints Principais

### Autenticação
- POST `/api/v1/login` - Login de usuário
- POST `/api/v1/signup` - Registro de usuário

### Usuários
- GET `/api/v1/usuarios/perfil` - Perfil do usuário
- PUT `/api/v1/usuarios/editar` - Editar perfil

### Cisterna
- GET `/api/v1/cisterna/dados-atuais` - Dados atuais
- GET `/api/v1/cisterna/historico` - Histórico de leituras

## Testes

Executar testes:
```bash
pytest
```
