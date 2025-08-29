from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from ....crud import usuario as crud_usuario
from ....schemas import usuario as schemas
from ....api.deps import get_db, get_current_user
from ....core.security import get_password_hash, verify_password
from ....models.usuario import Usuario

router = APIRouter()

@router.get("/perfil", 
              response_model=schemas.Usuario,
              status_code=status.HTTP_200_OK,
              summary="Obter Perfil do Usuário",
              response_description="Dados do perfil do usuário",
              tags=["usuários"])
def obter_perfil(
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    """
    Retorna o perfil completo do usuário autenticado.

    Returns:
        Usuario: Objeto contendo todos os dados do usuário
            - id: ID único do usuário
            - nome: Nome completo
            - email: Email do usuário
            - cpf: CPF do usuário
            - tipo: Tipo de usuário (comum/admin)
            - ativo: Status da conta
            
    Raises:
        HTTPException:
            - 401: Usuário não autenticado
            - 404: Usuário não encontrado
            
    Examples:
        >>> # Python
        >>> import requests
        >>> headers = {"Authorization": f"Bearer {token}"}
        >>> response = requests.get("http://localhost:8000/api/v1/usuarios/perfil", headers=headers)
        >>> perfil = response.json()
    """
    return current_user

@router.put("/editar-perfil", 
         response_model=schemas.Usuario,
         status_code=status.HTTP_200_OK,
         summary="Atualizar Perfil do Usuário",
         response_description="Perfil atualizado do usuário",
         tags=["usuários"])
def editar_perfil(
    dados_atualizacao: schemas.UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    """
    Atualiza os dados do perfil do usuário autenticado.
    
    Args:
        dados_atualizacao: Dados a serem atualizados
            - nome: Novo nome (opcional)
            - email: Novo email (opcional)
            - endereco: Novo endereço (opcional)
        current_user: Usuário atual (injetado via token)
        
    Returns:
        Usuario: Objeto com os dados atualizados do usuário
        
    Raises:
        HTTPException:
            - 401: Usuário não autenticado
            - 400: Dados inválidos
            - 409: Email já existe
            
    Examples:
        >>> # Python
        >>> import requests
        >>> headers = {"Authorization": f"Bearer {token}"}
        >>> dados = {
        ...     "nome": "Novo Nome",
        ...     "email": "novo@email.com",
        ...     "endereco": "Nova Rua, 123"
        ... }
        >>> response = requests.put(
        ...     "http://localhost:8000/api/v1/usuarios/editar-perfil",
        ...     headers=headers,
        ...     json=dados
        ... )
        >>> perfil_atualizado = response.json()
    - Se uma nova senha for fornecida, ela será hasheada antes de salvar
    """
    # Se estiver atualizando o email, verifica se já existe
    if dados_atualizacao.email and dados_atualizacao.email != current_user.email:
        usuario_existente = crud_usuario.get_usuario_by_email(db, email=dados_atualizacao.email)
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
):
    """
    Desativa a conta do usuário atual (soft delete).
    Requer a senha atual para confirmar a operação.
    """
    # Valida a senha antes de desativar
    if not verify_password(senha, current_user.senha):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha incorreta"
        )
    
    # Desativa o usuário
    crud_usuario.deactivate_usuario(db, usuario=current_user)
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)
