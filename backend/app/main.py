from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse, RedirectResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import Request
from backend.app.core.config import settings
from backend.app.api.v1 import api_router
from backend.app.api.deps import get_current_user
from backend.app.crud.usuario import get_usuario
from pathlib import Path
from sqlalchemy.orm import Session
from backend.app.api.deps import get_db
from backend.app.models.usuario import Usuario
from backend.app.models.local import Local
import warnings

app = FastAPI(
    title="Sensorium API",
    description="API do sistema Sensorium UFRPE",
    version="1.0.0",
)

# --- EXCEPTION HANDLERS ---
# Esses handlers garantem que erros acessem as páginas HTML personalizadas
# mas mantêm o comportamento JSON para a API.

BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BASE_DIR.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"

if TEMPLATES_DIR.exists():
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
else:
    # Fallback
    fallback = PROJECT_ROOT / "templates"
    if fallback.exists():
        templates = Jinja2Templates(directory=str(fallback))
    else:
        warnings.warn(f"Templates directory not found.")
        templates = Jinja2Templates(directory=str(TEMPLATES_DIR)) # Evita erro de variavel indefinida

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    # Se for uma requisição para a API, retorna JSON (comportamento padrão)
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
    
    # Se for erro 404 no navegador, mostra a página 404.html
    if exc.status_code == 404:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    
    # Outros erros HTTP (401, 403, etc) podem ser tratados aqui ou cair no padrão
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(500)
async def custom_500_handler(request: Request, exc: Exception):
    # Log do erro (pode ser melhorado com logger)
    print(f"Erro interno (500): {str(exc)}")
    
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"},
        )
        
    return templates.TemplateResponse("500.html", {"request": request}, status_code=500)


# Health check endpoint
@app.get("/health")
async def health(db: Session = Depends(get_db)):
    try:
        # Testa conexão com banco
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Database not available")

print("Health endpoint registered")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir os routers da API
app.include_router(api_router, prefix=settings.API_V1_STR)

print("API router included")

STATIC_DIR = PROJECT_ROOT / "static"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
else:
    warnings.warn(f"Static directory not found: {STATIC_DIR}. Skipping static mount.")

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
    return templates.TemplateResponse(
        "dashboard_usuario.html", 
        {
            "request": request
        }
    )

@app.get("/check_token.html", response_class=HTMLResponse)
async def check_token(request: Request):
    return templates.TemplateResponse("check_token.html", {"request": request})

@app.get("/test_token.html", response_class=HTMLResponse)
async def test_token(request: Request):
    return templates.TemplateResponse("test_token.html", {"request": request})

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
    
    # Obter todos os sensores
    sensores = db.query(Local).all()
    
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "usuarios": usuarios,
        "notificacoes": notificacoes,
        "configuracoes": configuracoes,
        "total_usuarios": total_usuarios,
        "total_notificacoes": total_notificacoes,
        "sensores": sensores
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