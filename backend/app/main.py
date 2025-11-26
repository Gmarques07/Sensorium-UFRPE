from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse, RedirectResponse
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

BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BASE_DIR.parent
STATIC_DIR = PROJECT_ROOT / "static"
TEMPLATES_DIR = PROJECT_ROOT / "templates"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
else:
    warnings.warn(f"Static directory not found: {STATIC_DIR}. Skipping static mount.")

if TEMPLATES_DIR.exists():
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
else:
    # Fallback: tenta diretório na raiz do projeto
    fallback = PROJECT_ROOT / "templates"
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

@app.get("/gerenciar_sensor/{sensor_id}", response_class=HTMLResponse)
async def gerenciar_sensor(request: Request, sensor_id: int, db: Session = Depends(get_db)):
    # Obter o sensor
    sensor = db.query(Local).filter(Local.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor não encontrado")

    # Obter usuários associados ao sensor
    from backend.app.crud import usuario_sensor as crud_usuario_sensor
    sensor_usuarios = crud_usuario_sensor.get_usuarios_do_sensor(db, sensor_id)

    # Converter para objetos de usuário
    usuarios_atribuidos = []
    for usuario_sensor in sensor_usuarios:
        usuario = db.query(Usuario).filter(Usuario.id == usuario_sensor.usuario_id).first()
        if usuario:
            usuarios_atribuidos.append(usuario)

    # Obter todos os usuários
    todos_usuarios = db.query(Usuario).all()

    return templates.TemplateResponse("gerenciar_sensor.html", {
        "request": request,
        "sensor": {
            "id": sensor.id,
            "nome": sensor.nome,
            "tipo": sensor.tipo,
            "descricao": sensor.descricao,
            "chave_api": sensor.chave_api
        },
        "usuarios_atribuidos": usuarios_atribuidos,
        "todos_usuarios": todos_usuarios
    })

@app.get("/dados_sensor/{sensor_id}", response_class=HTMLResponse)
async def dados_sensor(request: Request, sensor_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    # Obter o sensor
    sensor = db.query(Local).filter(Local.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor não encontrado")

    # Verificar associação do sensor com o usuário
    from backend.app.models.usuario_sensor import UsuarioSensor
    from sqlalchemy import and_
    assoc = db.query(UsuarioSensor).filter(
        and_(
            UsuarioSensor.usuario_id == current_user.id,
            UsuarioSensor.sensor_id == sensor_id
        )
    ).first()

    if not assoc:
        raise HTTPException(status_code=403, detail="Você não tem permissão para acessar este sensor")

    # Obter histórico de leituras (últimas 50)
    from backend.app.models.leitura import Leitura
    leituras = db.query(Leitura).filter(
        Leitura.dispositivo_id == sensor_id
    ).order_by(Leitura.data_registro.desc()).limit(50).all()

    return templates.TemplateResponse("dados_sensor.html", {
        "request": request,
        "sensor": {
            "id": sensor.id,
            "nome": sensor.nome,
            "tipo": sensor.tipo,
            "descricao": sensor.descricao,
            "chave_api": sensor.chave_api
        },
        "leituras": leituras
    })

@app.get("/dados_sensor/{sensor_id}", response_class=HTMLResponse)
async def dados_sensor(request: Request, sensor_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    # Obter o sensor
    sensor = db.query(Local).filter(Local.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor não encontrado")

    # Verificar associação do sensor com o usuário
    from backend.app.models.usuario_sensor import UsuarioSensor
    from sqlalchemy import and_
    assoc = db.query(UsuarioSensor).filter(
        and_(
            UsuarioSensor.usuario_id == current_user.id,
            UsuarioSensor.sensor_id == sensor_id
        )
    ).first()

    if not assoc:
        raise HTTPException(status_code=403, detail="Você não tem permissão para acessar este sensor")

    # Obter histórico de leituras (últimas 50)
    from backend.app.models.leitura import Leitura
    leituras = db.query(Leitura).filter(
        Leitura.dispositivo_id == sensor_id
    ).order_by(Leitura.data_registro.desc()).limit(50).all()

    return templates.TemplateResponse("dados_sensor.html", {
        "request": request,
        "sensor": {
            "id": sensor.id,
            "nome": sensor.nome,
            "tipo": sensor.tipo,
            "descricao": sensor.descricao,
            "chave_api": sensor.chave_api
        },
        "leituras": leituras
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