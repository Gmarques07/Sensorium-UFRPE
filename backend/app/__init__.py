from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from backend.app.api.v1 import api_router
from backend.app.core.docs import swagger_ui_config, tags_metadata, schemas_descriptions

app = FastAPI(
    title="Sensorium UFRPE API",
    description="""
    API do Sistema Sensorium UFRPE para monitoramento de cisternas.
    
    ## Funcionalidades

    * Autenticação de usuários via JWT
    * Gerenciamento de usuários
    * Monitoramento de cisternas
    * Sistema de notificações
    * Painel administrativo
    
    ## Links Úteis
    
    * [Documentação detalhada](/docs/API.md)
    * [Guia de instalação](/docs/INSTALL.md)
    * [Contribuição](/docs/CONTRIBUTING.md)
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=tags_metadata,
    **swagger_ui_config
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Sensorium UFRPE API",
        version="2.0.0",
        description="API do Sistema Sensorium UFRPE para monitoramento de cisternas",
        routes=app.routes,
    )
    
    # Configurações adicionais do OpenAPI
    openapi_schema["info"]["x-logo"] = {
        "url": "static/img/logo.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Incluir as rotas da API
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """
    Rota raiz que retorna informações básicas sobre a API.
    """
    return {
        "message": "Bem-vindo à API do Sensorium UFRPE",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }