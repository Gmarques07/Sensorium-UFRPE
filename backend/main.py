from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse
import uvicorn
from app.core.config import settings
import os

# Criar a aplicação principal que inclui a API
app = FastAPI(
    title="Sensorium UFRPE",
    description="Sistema de monitoramento de cisternas",
    version="1.0.0"
)

# Incluir os routers da API diretamente na aplicação principal
from app.api.v1 import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Configurar templates (apontando para o diretório correto)
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"))

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar arquivos estáticos
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")), name="static")

# Rotas para servir as páginas HTML
@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/index.html", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login_usuario.html", response_class=HTMLResponse)
async def login_usuario(request: Request):
    return templates.TemplateResponse("login_usuario.html", {"request": request})

@app.get("/login_admin.html", response_class=HTMLResponse)
async def login_admin(request: Request):
    return templates.TemplateResponse("login_admin.html", {"request": request})

@app.get("/cadastro.html", response_class=HTMLResponse)
async def cadastro(request: Request):
    return templates.TemplateResponse("cadastro.html", {"request": request})

@app.get("/dashboard_usuario.html", response_class=HTMLResponse)
async def dashboard_usuario(request: Request):
    # TODO: Implementar autenticação real
    # Por enquanto, vamos passar dados de exemplo
    usuario = {
        "nome": "Usuário Exemplo"
    }
    dispositivos = [
        {"dispositivo": "Dispositivo 1"},
        {"dispositivo": "Dispositivo 2"}
    ]
    
    # Dados de exemplo para pH
    ph_por_dispositivo = {
        "Dispositivo 1": {
            "atual": {
                "ph": 7.2,
                "data": "2023-01-01 10:00:00"
            },
            "historico": [
                {"ph": 7.0, "data": "2023-01-01 09:00:00"},
                {"ph": 7.1, "data": "2023-01-01 09:30:00"},
                {"ph": 7.2, "data": "2023-01-01 10:00:00"}
            ]
        },
        "Dispositivo 2": {
            "atual": {
                "ph": 6.8,
                "data": "2023-01-01 10:00:00"
            },
            "historico": [
                {"ph": 6.9, "data": "2023-01-01 09:00:00"},
                {"ph": 6.85, "data": "2023-01-01 09:30:00"},
                {"ph": 6.8, "data": "2023-01-01 10:00:00"}
            ]
        }
    }
    
    # Dados de exemplo para nível
    nivel_por_dispositivo = {
        "Dispositivo 1": {
            "atual": {
                "status": "ALTO",
                "boia": 1,
                "data": "2023-01-01 10:00:00"
            },
            "historico": [
                {"status": "ALTO", "data": "2023-01-01 09:00:00"},
                {"status": "ALTO", "data": "2023-01-01 09:30:00"},
                {"status": "ALTO", "data": "2023-01-01 10:00:00"}
            ]
        },
        "Dispositivo 2": {
            "atual": {
                "status": "BAIXO",
                "boia": 0,
                "data": "2023-01-01 10:00:00"
            },
            "historico": [
                {"status": "BAIXO", "data": "2023-01-01 09:00:00"},
                {"status": "BAIXO", "data": "2023-01-01 09:30:00"},
                {"status": "BAIXO", "data": "2023-01-01 10:00:00"}
            ]
        }
    }
    
    return templates.TemplateResponse("dashboard_usuario.html", {
        "request": request,
        "usuario": usuario,
        "dispositivos": dispositivos,
        "ph_por_dispositivo": ph_por_dispositivo,
        "nivel_por_dispositivo": nivel_por_dispositivo
    })

@app.get("/admin_dashboard.html", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    # TODO: Implementar autenticação real e buscar dados reais do banco
    # Por enquanto, vamos passar dados de exemplo
    usuarios = [
        {"id": 1, "nome": "Usuário 1", "cpf": "12345678901", "email": "usuario1@example.com", "endereco": "Endereço 1"},
        {"id": 2, "nome": "Usuário 2", "cpf": "12345678902", "email": "usuario2@example.com", "endereco": "Endereço 2"}
    ]
    
    notificacoes = [
        {"id": 1, "tipo": "Alerta", "titulo": "Nível baixo", "mensagem": "Nível da cisterna baixo", "data_criacao": "2023-01-01 10:00:00", "lida": False},
        {"id": 2, "tipo": "Info", "titulo": "Atualização", "mensagem": "Sistema atualizado", "data_criacao": "2023-01-01 09:00:00", "lida": True}
    ]
    
    configuracoes = [
        {"chave": "limite_ph_min", "valor": "6.5", "descricao": "Limite mínimo de pH", "tipo": "numero"},
        {"chave": "limite_ph_max", "valor": "8.5", "descricao": "Limite máximo de pH", "tipo": "numero"}
    ]
    
    total_usuarios = len(usuarios)
    total_notificacoes = len(notificacoes)
    
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "usuarios": usuarios,
        "notificacoes": notificacoes,
        "configuracoes": configuracoes,
        "total_usuarios": total_usuarios,
        "total_notificacoes": total_notificacoes
    })

@app.get("/sobre.html", response_class=HTMLResponse)
async def sobre(request: Request):
    return templates.TemplateResponse("sobre.html", {"request": request})

@app.get("/404.html", response_class=HTMLResponse)
async def not_found(request: Request):
    return templates.TemplateResponse("404.html", {"request": request})

@app.get("/500.html", response_class=HTMLResponse)
async def server_error(request: Request):
    return templates.TemplateResponse("500.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8002, reload=True)

