# Estrutura do Projeto Sensorium-UFRPE

## Organização das Pastas

```
Sensorium-UFRPE/
├── backend/                    # API FastAPI
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── auth.py
│   │   │   │   │   ├── usuarios.py
│   │   │   │   │   └── cisterna.py
│   │   │   │   └── __init__.py
│   │   │   └── __init__.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   └── database.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── models.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py
│   │   └── __init__.py
│   ├── tests/                 # Testes do backend
│   │   ├── __init__.py
│   │   ├── test_auth.py
│   │   ├── test_usuarios.py
│   │   └── test_cisterna.py
│   ├── main.py               # Ponto de entrada da API
│   ├── requirements.txt      # Dependências do backend
│   └── README.md            # Documentação do backend
│
├── database/                # Scripts do banco de dados
│   ├── migrations/
│   └── schemas/
│
└── README.md              # Documentação geral do projeto
```

## Separação de Responsabilidades

### Backend (/backend)
- API FastAPI
- Modelos de dados
- Lógica de negócios
- Autenticação e segurança
- Testes unitários e de integração

### Database (/database)
- Scripts SQL
- Migrações
- Schemas

## Configuração do Ambiente de Desenvolvimento

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

## Documentação da API
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
