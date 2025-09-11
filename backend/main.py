from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse
import uvicorn
from backend.app.core.config import settings
from backend.app.db.session import SessionLocal
from sqlalchemy.orm import Session
from backend.app import crud
from backend.app.models.usuario import Usuario
from backend.app.models.local import Local
import os

# Função para obter sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Criar a aplicação principal que inclui a API
app = FastAPI(
    title="Sensorium UFRPE",
    description="Sistema de monitoramento de cisternas",
    version="1.0.0"
)

# Incluir os routers da API diretamente na aplicação principal
from backend.app.api.v1 import api_router
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
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    # Buscar dados reais do banco de dados
    from backend.app import crud
    
    # Obter todos os usuários
    usuarios_objs = crud.usuario.get_multi(db, limit=100)
    usuarios = [
        {
            "id": u.id,
            "nome": u.nome,
            "email": u.email,
            "endereco": u.endereco
        } for u in usuarios_objs
    ]
    
    # Obter todas as notificações
    try:
        from sqlalchemy import text
        notificacoes_result = db.execute(
            text("SELECT * FROM notificacoes ORDER BY data_criacao DESC LIMIT 50")
        ).fetchall()
        notificacoes = [dict(n) for n in notificacoes_result]
    except Exception:
        notificacoes = []
    
    # Obter configurações
    try:
        configuracoes_objs = crud.admin.get_all_configuracoes(db, limit=100)
        configuracoes = [
            {
                "id": c.id,
                "chave": c.chave,
                "valor": c.valor,
                "descricao": c.descricao,
                "tipo": "numero"  # Tipo padrão para configurações
            } for c in configuracoes_objs
        ]
    except Exception:
        configuracoes = []
    
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

@app.get("/gerenciar_sensores/{usuario_id}", response_class=HTMLResponse)
async def gerenciar_sensores(request: Request, usuario_id: int, db: Session = Depends(get_db)):
    # Obter o usuário
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Obter sensores atribuídos ao usuário
    from backend.app.crud import usuario_sensor as crud_usuario_sensor
    usuario_sensores = crud_usuario_sensor.get_sensores_do_usuario(db, usuario_id)
    
    # Converter para objetos de sensor
    sensores_atribuidos = []
    for usuario_sensor in usuario_sensores:
        sensor = db.query(Local).filter(Local.id == usuario_sensor.sensor_id).first()
        if sensor:
            sensores_atribuidos.append(sensor)
    
    # Obter todos os sensores
    todos_sensores = db.query(Local).all()
    
    return templates.TemplateResponse("gerenciar_sensores.html", {
        "request": request,
        "usuario": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "endereco": usuario.endereco
        },
        "sensores_atribuidos": sensores_atribuidos,
        "todos_sensores": todos_sensores
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

@app.get("/health")
async def healthcheck():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
