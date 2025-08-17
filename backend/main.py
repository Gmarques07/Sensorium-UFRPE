from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse

app = FastAPI(
    title="Sensorium UFRPE",
    description="Sistema de monitoramento de cisternas",
    version="1.0.0"
)

# Configurar templates
templates = Jinja2Templates(directory="../templates")

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar arquivos estáticos
app.mount("/static", StaticFiles(directory="../static"), name="static")

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
    return templates.TemplateResponse("dashboard_usuario.html", {"request": request})

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

# APIs básicas de teste (sem banco de dados)
@app.get("/api/v1/test")
async def test_api():
    return {"message": "API funcionando!", "status": "ok"}

# APIs básicas de autenticação (simuladas - para desenvolvimento)
from fastapi import HTTPException, Form
from pydantic import BaseModel
import json
import hashlib
from datetime import datetime, timedelta

# Modelo para dados de usuário
class UsuarioData(BaseModel):
    nome: str
    cpf: str
    email: str
    endereco: str
    senha: str

# Simulação de "banco de dados" em memória (para desenvolvimento)
usuarios_db = []

def gerar_token_simples(cpf: str) -> str:
    """Gera um token simples para desenvolvimento"""
    data = f"{cpf}_{datetime.now().isoformat()}"
    return hashlib.md5(data.encode()).hexdigest()

def hash_senha(senha: str) -> str:
    """Hash simples da senha"""
    return hashlib.sha256(senha.encode()).hexdigest()

@app.post("/api/v1/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """
    Endpoint de login que simula autenticação
    """
    # Buscar usuário na "base de dados" simulada
    usuario_encontrado = None
    for user in usuarios_db:
        if user["cpf"] == username:
            usuario_encontrado = user
            break
    
    if not usuario_encontrado:
        raise HTTPException(status_code=401, detail="CPF ou senha incorretos")
    
    # Verificar senha
    senha_hash = hash_senha(password)
    if usuario_encontrado["senha"] != senha_hash:
        raise HTTPException(status_code=401, detail="CPF ou senha incorretos")
    
    # Gerar token
    token = gerar_token_simples(username)
    
    return {
        "access_token": token,
        "token_type": "bearer"
    }

@app.post("/api/v1/auth/registro")
async def registro(usuario: UsuarioData):
    """
    Endpoint de registro que simula cadastro
    """
    # Verificar se CPF já existe
    for user in usuarios_db:
        if user["cpf"] == usuario.cpf:
            raise HTTPException(status_code=400, detail="CPF já cadastrado")
        if user["email"] == usuario.email:
            raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Adicionar usuário à "base de dados"
    novo_usuario = {
        "nome": usuario.nome,
        "cpf": usuario.cpf,
        "email": usuario.email,
        "endereco": usuario.endereco,
        "senha": hash_senha(usuario.senha),
        "data_cadastro": datetime.now().isoformat()
    }
    
    usuarios_db.append(novo_usuario)
    
    # Gerar token
    token = gerar_token_simples(usuario.cpf)
    
    return {
        "access_token": token,
        "token_type": "bearer"
    }

# Endpoint para listar usuários (para debug)
@app.get("/api/v1/debug/usuarios")
async def listar_usuarios_debug():
    return {
        "total": len(usuarios_db),
        "usuarios": [{"nome": u["nome"], "cpf": u["cpf"], "email": u["email"]} for u in usuarios_db]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

