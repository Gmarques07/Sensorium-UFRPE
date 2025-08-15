# Documentação da API - Sensorium UFRPE

## Visão Geral

Esta documentação descreve detalhadamente a API RESTful do Sistema Sensorium UFRPE versão 2.0.0. A API foi desenvolvida usando FastAPI e segue as melhores práticas de design de APIs RESTful.

## Autenticação

### JWT (JSON Web Token)

A API utiliza autenticação baseada em JWT. Para obter um token:

1. Faça uma requisição POST para `/api/v1/auth/login`
2. Use o token retornado no header `Authorization` de todas as requisições subsequentes

Exemplo de header:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Endpoints Detalhados

### Autenticação

#### POST /api/v1/auth/login
Login de usuário.

**Request:**
```json
{
    "email": "string",
    "password": "string"
}
```

**Response:**
```json
{
    "access_token": "string",
    "token_type": "bearer"
}
```

### Usuários

#### GET /api/v1/usuarios/perfil
Retorna o perfil do usuário autenticado.

**Response:**
```json
{
    "id": "integer",
    "nome": "string",
    "email": "string",
    "cpf": "string",
    "tipo": "string"
}
```

### Cisterna

#### GET /api/v1/cisterna/dados-atuais
Retorna os dados atuais da cisterna.

**Response:**
```json
{
    "nivel_agua": "float",
    "ph": "float",
    "ultima_leitura": "datetime",
    "status": "string"
}
```

### Notificações

#### GET /api/v1/notificacoes/listar
Lista todas as notificações do usuário.

**Response:**
```json
{
    "notificacoes": [
        {
            "id": "integer",
            "mensagem": "string",
            "tipo": "string",
            "data_criacao": "datetime",
            "lida": "boolean"
        }
    ]
}
```

## Códigos de Status

- 200: Sucesso
- 201: Criado com sucesso
- 400: Erro de validação
- 401: Não autorizado
- 403: Acesso proibido
- 404: Recurso não encontrado
- 500: Erro interno do servidor

## Versionamento

A API utiliza versionamento via URL (/api/v1/). As principais mudanças de versão serão documentadas aqui.

## Rate Limiting

A API implementa rate limiting para proteger contra abusos:
- 100 requisições por minuto para endpoints públicos
- 1000 requisições por minuto para endpoints autenticados

## Webhooks

A API suporta webhooks para notificações em tempo real. Configure webhooks através do painel administrativo.

## Ambiente de Testes

Um ambiente de testes está disponível em:
```
https://api-test.sensorium-ufrpe.com
```

## Exemplos de Código

### Python
```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={
        "email": "usuario@email.com",
        "password": "senha123"
    }
)
token = response.json()["access_token"]

# Obter dados da cisterna
headers = {"Authorization": f"Bearer {token}"}
dados = requests.get(
    "http://localhost:8000/api/v1/cisterna/dados-atuais",
    headers=headers
).json()
```

### JavaScript
```javascript
// Login
const login = async () => {
    const response = await fetch("http://localhost:8000/api/v1/auth/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            email: "usuario@email.com",
            password: "senha123"
        })
    });
    const data = await response.json();
    return data.access_token;
};

// Obter dados da cisterna
const getDadosCisterna = async (token) => {
    const response = await fetch("http://localhost:8000/api/v1/cisterna/dados-atuais", {
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });
    return await response.json();
};
```

## Boas Práticas

1. Sempre utilize HTTPS em produção
2. Armazene tokens de forma segura
3. Implemente retry com backoff exponencial
4. Valide todos os inputs antes de enviar
5. Trate erros adequadamente

## Suporte

Para suporte técnico:
- Email: suporte@sensorium-ufrpe.com
- Issues: GitHub
- Discord: https://discord.gg/sensorium-ufrpe
