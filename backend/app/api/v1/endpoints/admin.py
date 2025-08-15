from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ....crud import admin as crud_admin
from ....crud import usuario as crud_usuario
from ....schemas import admin as schemas
from ....api.deps import get_db, get_current_admin
from ....models.usuario import Usuario

router = APIRouter()

@router.get("/dashboard", response_model=schemas.AdminDashboard)
async def get_dashboard(
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin)
) -> Any:
    """
    Retorna dados para o dashboard administrativo.
    """
    # Obtém estatísticas gerais
    stats = crud_admin.get_dashboard_stats(db)
    
    # Obtém últimas notificações
    ultimas_notificacoes = db.execute(
        """SELECT * FROM notificacoes 
           ORDER BY data_criacao DESC LIMIT 5"""
    ).fetchall()
    
    # Obtém usuários recentes
    usuarios_recentes = crud_usuario.get_multi(db, limit=5)
    
    # Obtém configurações
    configuracoes = crud_admin.get_all_configuracoes(db, limit=10)
    
    return {
        "stats": stats,
        "ultimas_notificacoes": [dict(n) for n in ultimas_notificacoes],
        "usuarios_recentes": usuarios_recentes,
        "configuracoes": configuracoes
    }

@router.get("/usuarios", response_model=List[Usuario])
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
) -> Any:
    """
    Remove uma configuração do sistema.
    """
    if not crud_admin.delete_configuracao(db, chave):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuração não encontrada"
        )
    return None
