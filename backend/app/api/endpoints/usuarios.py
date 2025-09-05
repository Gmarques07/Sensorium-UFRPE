from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.api import deps
from app.core.security import get_password_hash
from app.core.auth import get_current_user

router = APIRouter()

@router.get("/perfil", response_model=schemas.Usuario)
def ler_perfil_usuario(
    current_user: models.Usuario = Depends(get_current_user)
) -> Any:
    """
    Recupera o perfil do usuário logado.
    """
    return current_user

@router.put("/editar-perfil", response_model=schemas.Usuario)
def atualizar_perfil(
    *,
    db: Session = Depends(deps.get_db),
    usuario_in: schemas.UsuarioUpdate,
    current_user: models.Usuario = Depends(get_current_user)
) -> Any:
    """
    Atualiza os dados do usuário logado.
    """
    usuario = crud.usuario.update_usuario(db, usuario=current_user, usuario_in=usuario_in)
    return usuario

@router.get("/{email}", response_model=schemas.Usuario)
def ler_usuario_por_email(
    email: str,
    db: Session = Depends(deps.get_db),
    current_user: models.Usuario = Depends(get_current_user)
) -> Any:
    """
    Recupera um usuário pelo email.
    """
    usuario = crud.usuario.get_usuario_by_email(db, email=email)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    if usuario.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado a acessar este perfil"
        )
    return usuario

@router.delete("/{email}", response_model=bool)
def excluir_usuario(
    email: str,
    db: Session = Depends(deps.get_db),
    current_user: models.Usuario = Depends(get_current_user)
) -> Any:
    """
    Exclui o usuário.
    """
    usuario = crud.usuario.get_usuario_by_email(db, email=email)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    if usuario.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado a excluir este perfil"
        )
    return crud.usuario.delete_usuario(db, usuario=usuario)
