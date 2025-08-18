# Sistema de Gerenciamento de Cisternas

Este é um sistema web para gerenciamento de cisternas, monitoramento de níveis de água e qualidade (pH). O projeto foi totalmente migrado para uma arquitetura moderna utilizando FastAPI.

## Funcionalidades Principais

### Para Usuários
- Cadastro e login de usuários
- Solicitação de pedidos de água
- Monitoramento do status dos pedidos
- Visualização de níveis de água e pH da cisterna
- Upload e análise de imagens para detecção de rachaduras
- Recebimento de comunicados e notificações

### Para Empresas
- Cadastro e login de empresas
- Gerenciamento de pedidos recebidos
- Monitoramento de cisternas
- Análise de imagens para detecção de rachaduras
- Envio de comunicados aos usuários
- Dashboard com informações relevantes

### Para Administradores
- Painel administrativo completo
- Gerenciamento de usuários e empresas
- Monitoramento de pedidos
- Configurações do sistema
- Sistema de notificações

## Tecnologias Utilizadas

### Backend (API)
- FastAPI (Framework Web moderno e assíncrono)
- Pydantic (Validação de dados)
- SQLAlchemy (ORM)
- JWT (Autenticação)
- MySQL (Banco de Dados)

### Frontend (Interface Web)
- HTML/CSS/JavaScript
- Bootstrap (Framework CSS)
- Jinja2 (Templates)

### Outras
- OpenCV (Processamento de Imagens) (descontinuado)
- Docker (Containerização - opcional)

## Pré-requisitos

- Python 3.7+
- MySQL Server
- Bibliotecas Python (listadas em backend/requirements.txt)

## Instalação

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITORIO]
```

2. Navegue até o diretório do backend:
```bash
cd backend
```

3. Crie um ambiente virtual (opcional mas recomendado):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

5. Configure as variáveis de ambiente:
```bash
cp .env.example .env
```
Edite o arquivo `.env` com as configurações do seu banco de dados.

6. Configure o MySQL Server (verifique as instruções detalhadas em `backend/README.md`)

7. Inicialize o banco de dados:
```bash
python init_db.py
```

8. Inicie o servidor:
```bash
python start_server.py --reload
```

## Estrutura do Projeto

```
Sensorium-UFRPE/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       └── __init__.py
│   │   ├── core/
│   │   ├── crud/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── main.py
│   ├── static/
│   ├── templates/
│   ├── init_db.py
│   ├── main.py
│   ├── start_server.py
│   ├── check_mysql.py
│   ├── requirements.txt
│   └── .env.example
├── static/
├── templates/
├── ATUALIZACAO_MIGRACAO.md
├── MIGRACAO_FLASK_FASTAPI.md
├── README.md
└── requirements.txt
```

## Documentação da API

A documentação automática da API está disponível em:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Funcionalidades de Segurança

- Autenticação JWT
- Senhas criptografadas com bcrypt
- Controle de acesso baseado em perfis
- Validação de dados de entrada com Pydantic
- Proteção contra uploads maliciosos
- CORS configurado

## Processamento de Imagens

O sistema utiliza OpenCV para:
- Detecção automática de rachaduras
- Análise de objetos nas imagens
- Processamento e armazenamento seguro de uploads

## Contribuição

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## Suporte

Para suporte, abra uma issue no repositório ou consulte a documentação em `backend/README.md`.
