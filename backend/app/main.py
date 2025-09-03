from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse, RedirectResponse
from fastapi import Request
from app.core.config import settings
from app.api.v1 import api_router
from app.api.deps import get_current_user
from app.crud.usuario import get_usuario
from pathlib import Path
import warnings

app = FastAPI(
    title="Sensorium API",
    description="API do sistema Sensorium UFRPE",
    version="1.0.0",
)

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

# Configurar arquivos estáticos e templates
# Calcular diretórios estáticos e de templates dinamicamente para
# funcionar tanto em desenvolvimento quanto dentro do container Docker.
BASE_DIR = Path(__file__).resolve().parents[1]
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
else:
    warnings.warn(f"Static directory not found: {STATIC_DIR}. Skipping static mount.")

if TEMPLATES_DIR.exists():
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
else:
    # Fallback: tenta diretório relativo ao pacote app
    fallback = Path(__file__).resolve().parents[0] / "templates"
    if fallback.exists():
        templates = Jinja2Templates(directory=str(fallback))
    else:
        warnings.warn(f"Templates directory not found: {TEMPLATES_DIR} or {fallback}.")
        templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

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
async def admin_dashboard(request: Request):
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})

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
async def health():
    return {"status": "ok"}
