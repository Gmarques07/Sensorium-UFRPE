from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ....crud import usuario as crud_usuario
from ....schemas import usuario as schemas
from ....api.deps import get_db, get_current_user
from ....core.security import get_password_hash, verify_password
from ....models.usuario import Usuario

router = APIRouter()

@router.get("/perfil", response_model=schemas.Usuario)
def obter_perfil(
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    """
    Retorna o perfil do usuário autenticado.
    """
    return current_user

@router.put("/editar-perfil", response_model=schemas.Usuario)
def editar_perfil(
    dados_atualizacao: schemas.UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    """
    Atualiza os dados do perfil do usuário autenticado.
    
    - Permite atualizar nome, email e endereço
    - Se uma nova senha for fornecida, ela será hasheada antes de salvar
    """
    # Se estiver atualizando o email, verifica se já existe
    if dados_atualizacao.email and dados_atualizacao.email != current_user.email:
        usuario_existente = crud_usuario.get_by_email(db, email=dados_atualizacao.email)
        if usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este email já está em uso"
            )
    
    # Se uma nova senha foi fornecida, faz o hash
    if dados_atualizacao.senha:
        dados_atualizacao.senha = get_password_hash(dados_atualizacao.senha)
    
    usuario = crud_usuario.update(
        db, 
        db_obj=current_user,
        obj_in=dados_atualizacao
    )
    return usuario

@router.post("/validar-senha")
def validar_senha(
    senha: str,
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    """
    Valida a senha atual do usuário.
    Útil antes de realizar operações sensíveis.
    """
    if not verify_password(senha, current_user.senha):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha incorreta"
        )
    return {"valid": True}

@router.delete("/excluir-conta", status_code=status.HTTP_204_NO_CONTENT)
def excluir_conta(
    senha: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    """
    Exclui a conta do usuário atual.
    Requer a senha atual para confirmar a operação.
    """
    # Valida a senha antes de excluir
    if not verify_password(senha, current_user.senha):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha incorreta"
        )
    
    # Exclui o usuário
    crud_usuario.delete(db, id=current_user.id)
    
    return None
