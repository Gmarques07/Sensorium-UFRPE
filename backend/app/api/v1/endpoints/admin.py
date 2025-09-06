from typing import Any, List
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.crud import admin as crud_admin
from backend.app.crud import usuario as crud_usuario
from backend.app.crud import usuario_sensor as crud_usuario_sensor
from backend.app.schemas import admin as schemas
from backend.app.schemas import usuario as usuario_schemas
from backend.app.schemas import usuario_sensor as usuario_sensor_schemas
from backend.app.schemas import auth as auth_schemas
from backend.app.schemas import local as local_schemas
from backend.app.api.deps import get_db, get_current_admin
from backend.app.models.usuario import Usuario
from backend.app.models.admin import Admin
from backend.app.models.local import Local
from backend.app.core.security import create_access_token, verify_password
from backend.app.core.config import settings
from backend.app.core.limiter import rate_limit

router = APIRouter()

@router.post("/login", response_model=auth_schemas.Token, status_code=status.HTTP_200_OK,
             summary="Login de administrador",
             description="Endpoint para autenticação de administrador usando OAuth2 com JWT",
             response_description="Token de acesso JWT",
             tags=["admin"])
async def admin_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    __rl: None = Depends(rate_limit(5, 60, "login-admin"))
) -> Any:
    """
    Realiza o login do administrador usando OAuth2 com JWT.
    
    Args:
        form_data: Formulário com username (email) e senha
        db: Sessão do banco de dados
        
    Returns:
        Token JWT para autenticação
        
    Raises:
        HTTPException:
            - 401: Credenciais inválidas
            - 400: Administrador inativo
    """
    # Busca o admin pelo email
    admin = db.query(Admin).filter(Admin.email == form_data.username).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verifica a senha
    if not admin.verificar_senha(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Gera o token de acesso
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.email, "type": "admin"}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get(
    "/dashboard",
    response_model=schemas.AdminDashboard,
    status_code=status.HTTP_200_OK,
    summary="Dashboard Administrativo",
    response_description="Dados e estatísticas do dashboard admin",
    tags=["admin"]
)
async def get_dashboard(
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin)
) -> Any:
    """
    Retorna dados consolidados para o dashboard administrativo.
    
    Returns:
        AdminDashboard: Objeto com dados do dashboard
            - total_usuarios: Número total de usuários
            - usuarios_ativos: Número de usuários ativos
            - total_notificacoes: Total de notificações
            - alertas_nao_lidos: Número de alertas não lidos
            - ultima_atualizacao: Data da última atualização
            - usuarios_recentes: Lista dos últimos usuários cadastrados
            - ultimas_notificacoes: Lista das últimas notificações
            - estatisticas_cisterna: Dados estatísticos da cisterna
            
    Raises:
        HTTPException:
            - 401: Usuário não autenticado
            - 403: Usuário não é administrador
            
    Examples:
        >>> # Python
        >>> import requests
        >>> headers = {"Authorization": f"Bearer {token}"}
        >>> response = requests.get(
        ...     "http://localhost:8000/api/v1/admin/dashboard",
        ...     headers=headers
        ... )
        >>> dashboard = response.json()
    """
    # Obtém estatísticas gerais
    stats = crud_admin.get_dashboard_stats(db)
    
    # Obtém últimas notificações
    try:
        ultimas_notificacoes = db.execute(
            text("""SELECT * FROM notificacoes 
               ORDER BY data_criacao DESC LIMIT 5""")
        ).fetchall()
        ultimas_notificacoes_list = [dict(n) for n in ultimas_notificacoes]
    except Exception:
        ultimas_notificacoes_list = []
    
    # Obtém usuários recentes
    try:
        usuarios_objs = crud_usuario.get_multi(db, limit=5)
        usuarios_recentes = [
            {
                "id": u.id,
                "nome": u.nome,
                "email": u.email,
                "endereco": u.endereco,
                "data_criacao": u.created_at.isoformat() if u.created_at else None
            } for u in usuarios_objs
        ]
    except Exception as e:
        print(f"Erro ao obter usuários recentes: {e}")
        usuarios_recentes = []
    
    # Obtém configurações
    try:
        config_objs = crud_admin.get_all_configuracoes(db, limit=10)
        configuracoes = [
            {
                "id": c.id,
                "chave": c.chave,
                "valor": c.valor,
                "descricao": c.descricao,
                "data_criacao": c.data_criacao
            } for c in config_objs
        ]
    except Exception:
        configuracoes = []
    
    return {
        "stats": stats,
        "ultimas_notificacoes": ultimas_notificacoes_list,
        "usuarios_recentes": usuarios_recentes,
        "configuracoes": configuracoes
    }

@router.get("/usuarios", response_model=List[usuario_schemas.Usuario])
async def listar_usuarios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin)
) -> Any:
    """
    Lista todos os usuários do sistema.
    """
    usuarios = crud_usuario.get_multi(db, skip=skip, limit=limit)
    return usuarios

@router.get("/sensores", response_model=List[local_schemas.Local])
async def listar_sensores(
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin)
) -> Any:
    """
    Lista todos os sensores do sistema.
    """
    return db.query(Local).all()

@router.get("/usuarios/{usuario_id}/sensores", response_model=List[local_schemas.Local])
async def listar_sensores_do_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin)
) -> Any:
    """
    Lista todos os sensores atribuídos a um usuário específico.
    """
    # Verifica se o usuário existe
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Obtém os relacionamentos usuário-sensor
    usuario_sensores = crud_usuario_sensor.get_sensores_do_usuario(db, usuario_id)
    
    # Obtém os sensores correspondentes
    sensores = []
    for usuario_sensor in usuario_sensores:
        sensor = db.query(Local).filter(Local.id == usuario_sensor.local_id).first()
        if sensor:
            sensores.append(sensor)
    
    return sensores


@router.post("/usuarios/{usuario_id}/sensores", response_model=usuario_sensor_schemas.UsuarioSensor)
async def atribuir_sensor_a_usuario(
    usuario_id: int,
    sensor_id: int = Query(..., description="ID do sensor a ser atribuído"),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin)
) -> Any:
    """
    Atribui um sensor a um usuário.
    """
    # Verifica se o usuário existe
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Verifica se o sensor existe
    sensor = db.query(Local).filter(Local.id == sensor_id).first()
    if not sensor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sensor não encontrado"
        )
    
    # Verifica se o relacionamento já existe
    usuario_sensor = crud_usuario_sensor.get_usuario_sensor(db, usuario_id, sensor_id)
    if usuario_sensor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sensor já atribuído a este usuário"
        )
    
    # Cria o relacionamento
    usuario_sensor_create = usuario_sensor_schemas.UsuarioSensorCreate(
        usuario_id=usuario_id,
        local_id=sensor_id
    )
    return crud_usuario_sensor.create_usuario_sensor(db, usuario_sensor_create)

@router.delete("/usuarios/{usuario_id}/sensores/{sensor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover_sensor_de_usuario(
    usuario_id: int,
    sensor_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin)
) -> None:
    """
    Remove um sensor de um usuário.
    """
    # Verifica se o usuário existe
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Verifica se o sensor existe
    sensor = db.query(Local).filter(Local.id == sensor_id).first()
    if not sensor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sensor não encontrado"
        )
    
    # Remove o relacionamento
    if not crud_usuario_sensor.delete_usuario_sensor(db, usuario_id, sensor_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relacionamento usuário-sensor não encontrado"
        )
    
    return None

@router.delete("/usuarios/{usuario_id}/sensores", status_code=status.HTTP_204_NO_CONTENT)
async def remover_todos_sensores_do_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin)
) -> None:
    """
    Remove todos os sensores atribuídos a um usuário.
    """
    # Verifica se o usuário existe
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Remove todos os relacionamentos
    crud_usuario_sensor.delete_all_sensores_do_usuario(db, usuario_id)
    
    return None

@router.get("/configuracoes", response_model=List[schemas.Configuracao])
async def listar_configuracoes(
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin)
) -> Any:
    """
    Lista todas as configurações do sistema.
    """
    return crud_admin.get_all_configuracoes(db)

@router.post("/configuracoes", response_model=schemas.Configuracao)
async def criar_configuracao(
    config: schemas.ConfiguracaoCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin)
) -> Any:
    """
    Cria uma nova configuração no sistema.
    """
    # Verifica se a configuração já existe
    if crud_admin.get_configuracao(db, config.chave):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Configuração já existe"
        )
    return crud_admin.create_configuracao(db, config)

@router.put("/configuracoes/{chave}", response_model=schemas.Configuracao)
async def atualizar_configuracao(
    chave: str,
    config_in: schemas.ConfiguracaoUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin)
) -> Any:
    """
    Atualiza uma configuração existente.
    """
    config = crud_admin.update_configuracao(db, chave, config_in)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuração não encontrada"
        )
    return config

@router.delete("/configuracoes/{chave}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_configuracao(
    chave: str,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin)
) -> None:
    """
    Remove uma configuração do sistema.
    """
    if not crud_admin.delete_configuracao(db, chave):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuração não encontrada"
        )
    return None