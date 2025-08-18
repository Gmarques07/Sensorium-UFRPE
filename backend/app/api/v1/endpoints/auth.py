from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ....crud import usuario as crud_usuario
from ....schemas import auth as schemas_auth
from ....core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    verify_token
)
from ....api.deps import get_db
from ....core.config import settings
from ....models.usuario import Usuario

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.post("/login", response_model=schemas_auth.Token, status_code=status.HTTP_200_OK,
             summary="Autenticação de usuário",
             description="Endpoint para autenticação de usuário usando OAuth2 com JWT",
             response_description="Token de acesso JWT")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    Realiza o login do usuário usando OAuth2 com JWT.
    
    Args:
        form_data: Formulário com username (CPF) e senha
        db: Sessão do banco de dados
        
    Returns:
        Token JWT para autenticação
        
    Raises:
        HTTPException:
            - 401: Credenciais inválidas
            - 400: Usuário inativo
    
    Exemplos:
        >>> # Usando curl
        >>> curl -X POST "http://localhost:8000/api/v1/auth/login" \
        >>>      -H "Content-Type: application/x-www-form-urlencoded" \
        >>>      -d "username=12345678900&password=minhasenha123"
        
        >>> # Usando Python requests
        >>> import requests
        >>> response = requests.post(
        >>>     "http://localhost:8000/api/v1/auth/login",
        >>>     data={"username": "12345678900", "password": "minhasenha123"}
        >>> )
        >>> token = response.json()["access_token"]
        db: Sessão do banco de dados
        
    Returns:
        Token de acesso JWT
        
    Raises:
        HTTPException: Se as credenciais forem inválidas
    """
    usuario = crud_usuario.get_usuario_by_cpf(db, cpf=form_data.username)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="CPF ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="CPF ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": usuario.cpf}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/registro", response_model=schemas_auth.Token)
async def registro(
    usuario_in: schemas_auth.RegistroUsuario,
    db: Session = Depends(get_db)
) -> Any:
    """
    Registra um novo usuário e retorna um token de acesso.
    """
    # Verifica se o CPF já existe
    if crud_usuario.get_usuario_by_cpf(db, cpf=usuario_in.cpf):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF já cadastrado"
        )
    
    # Verifica se o email já existe
    if crud_usuario.get_usuario_by_email(db, email=usuario_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Cria o usuário
    usuario = crud_usuario.create_usuario(db, usuario=usuario_in)
    
    # Gera o token de acesso
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": usuario.cpf}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/recuperar-senha")
async def recuperar_senha(
    email_in: schemas_auth.RecuperacaoSenha,
    db: Session = Depends(get_db)
) -> Any:
    """
    Inicia o processo de recuperação de senha.
    Envia um email com um token de recuperação.
    """
    usuario = crud_usuario.get_usuario_by_email(db, email=email_in.email)
    if not usuario:
        # Sempre retorne sucesso para evitar enumeração de emails
        return {"message": "Se o email existir, você receberá as instruções de recuperação"}
    
    # Gera um token de recuperação
    reset_token = create_access_token(
        data={"sub": usuario.cpf, "type": "password_reset"},
        expires_delta=timedelta(hours=1)
    )
    
    # TODO: Implementar envio de email
    # Por enquanto, apenas retorna o token (apenas para desenvolvimento)
    if settings.ENVIRONMENT == "development":
        return {"reset_token": reset_token}
    
    return {"message": "Se o email existir, você receberá as instruções de recuperação"}

@router.post("/resetar-senha")
async def resetar_senha(
    reset_data: schemas_auth.ResetarSenha,
    db: Session = Depends(get_db)
) -> Any:
    """
    Reseta a senha do usuário usando um token de recuperação.
    """
    token_data = verify_token(reset_data.token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido ou expirado"
        )
    
    usuario = crud_usuario.get_usuario_by_cpf(db, cpf=token_data.cpf)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Atualiza a senha
    hashed_password = get_password_hash(reset_data.nova_senha)
    crud_usuario.update_password(db, usuario=usuario, new_password=hashed_password)
    
    return {"message": "Senha atualizada com sucesso"}
