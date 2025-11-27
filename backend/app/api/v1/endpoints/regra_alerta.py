from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ....crud import regra_alerta as crud_regra_alerta
from ....schemas import regra_alerta as schemas
from ....api.deps import get_db, get_current_user_from_cookie
from ....models.usuario import Usuario

router = APIRouter()

@router.get("/", response_model=List[schemas.RegraAlerta])
def listar_regras_alerta(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """
    Retorna uma lista paginada das regras de alerta do usuário atual.
    """
    regras = crud_regra_alerta.get_regras_alerta_por_usuario(
        db, current_user.email, skip=skip, limit=limit
    )
    return regras

@router.post("/", response_model=schemas.RegraAlerta, status_code=status.HTTP_201_CREATED)
def criar_regra_alerta(
    regra: schemas.RegraAlertaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """
    Cria uma nova regra de alerta para o usuário autenticado.
    """
    # Verificar se o usuário tem permissão para acessar este local
    from ....crud.usuario_sensor import get_sensores_do_usuario
    sensores_usuario = get_sensores_do_usuario(db, current_user.id)
    sensor_ids = [us.sensor_id for us in sensores_usuario]
    
    if regra.local_id not in sensor_ids:
        raise HTTPException(
            status_code=403, 
            detail="Você não tem permissão para criar regras para este sensor"
        )
    
    # Verificar se o usuário está tentando criar uma regra para si mesmo
    if regra.usuario_email != current_user.email:
        raise HTTPException(
            status_code=403, 
            detail="Você só pode criar regras para si mesmo"
        )
    
    return crud_regra_alerta.create_regra_alerta(db, regra)

@router.get("/{regra_id}", response_model=schemas.RegraAlerta)
def obter_regra_alerta(
    regra_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """
    Retorna uma regra de alerta específica.
    """
    regra = crud_regra_alerta.get_regra_alerta(db, regra_id)
    
    if not regra:
        raise HTTPException(status_code=404, detail="Regra de alerta não encontrada")
    
    if regra.usuario_email != current_user.email:
        raise HTTPException(status_code=403, detail="Acesso não autorizado")
    
    return regra

@router.put("/{regra_id}", response_model=schemas.RegraAlerta)
def atualizar_regra_alerta(
    regra_id: int,
    regra: schemas.RegraAlertaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """
    Atualiza uma regra de alerta existente.
    """
    db_regra = crud_regra_alerta.get_regra_alerta(db, regra_id)
    
    if not db_regra:
        raise HTTPException(status_code=404, detail="Regra de alerta não encontrada")
    
    if db_regra.usuario_email != current_user.email:
        raise HTTPException(status_code=403, detail="Acesso não autorizado")
    
    return crud_regra_alerta.update_regra_alerta(db, regra_id, regra)

@router.delete("/{regra_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_regra_alerta(
    regra_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """
    Deleta uma regra de alerta existente.
    """
    db_regra = crud_regra_alerta.get_regra_alerta(db, regra_id)
    
    if not db_regra:
        raise HTTPException(status_code=404, detail="Regra de alerta não encontrada")
    
    if db_regra.usuario_email != current_user.email:
        raise HTTPException(status_code=403, detail="Acesso não autorizado")
    
    success = crud_regra_alerta.delete_regra_alerta(db, regra_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Regra de alerta não encontrada")
    
    return