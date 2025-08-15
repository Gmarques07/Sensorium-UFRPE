"""
Configurações do Swagger UI para a API do Sensorium UFRPE.
"""

swagger_ui_config = {
    "swagger_ui_parameters": {
        "docExpansion": "none",
        "deepLinking": True,
        "persistAuthorization": True,
        "displayRequestDuration": True,
        "filter": True,
        "syntaxHighlight.theme": "monokai"
    },
    "swagger_ui_oauth2_config": {
        "usePkceWithAuthorizationCodeGrant": True,
        "clientId": "sensorium-web"
    }
}

# Tags para agrupar endpoints na documentação
tags_metadata = [
    {
        "name": "autenticação",
        "description": "Operações relacionadas à autenticação de usuários",
    },
    {
        "name": "usuários",
        "description": "Gerenciamento de usuários e perfis",
    },
    {
        "name": "cisterna",
        "description": "Endpoints para monitoramento de cisternas",
    },
    {
        "name": "notificações",
        "description": "Sistema de notificações e alertas",
    },
    {
        "name": "admin",
        "description": "Funcionalidades administrativas",
        "externalDocs": {
            "description": "Manual do Administrador",
            "url": "/docs/admin",
        },
    },
]

# Descrições dos modelos de dados
schemas_descriptions = {
    "Usuario": "Modelo de usuário do sistema",
    "Cisterna": "Dados de monitoramento da cisterna",
    "Notificacao": "Notificações e alertas do sistema",
    "Token": "Token de autenticação JWT",
}
