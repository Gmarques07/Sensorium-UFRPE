from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.app.crud import usuario as crud_usuario
from backend.app.schemas import auth as schemas_auth
from backend.app.schemas.usuario import UsuarioCreate
from backend.app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    verify_token
)
from backend.app.api.deps import get_db
from backend.app.core.limiter import rate_limit
from backend.app.core.config import settings
from backend.app.models.usuario import Usuario

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.post("/login", response_model=schemas_auth.Token, status_code=status.HTTP_200_OK,
             summary="Autenticação de usuário",
             description="Endpoint para autenticação de usuário usando email e senha",
             response_description="Token de acesso JWT")
async def login(
    response: Response,
    login_data: schemas_auth.Login,
    db: Session = Depends(get_db),
    __rl: None = Depends(rate_limit(5, 60, "login"))
) -> Any:
    """
    Realiza o login do usuário usando email e senha.
    
    Args:
        login_data: Dados de login contendo email e senha
        db: Sessão do banco de dados
        
    Returns:
        Token JWT para autenticação
        
    Raises:
        HTTPException:
            - 401: Credenciais inválidas
            - 400: Usuário inativo
    
    Exemplos:
        >>> # Usando curl
        >>> curl -X POST "http://localhost:8000/api/v1/auth/login" \\
        >>>      -H "Content-Type: application/json" \\
        >>>      -d '{"email": "usuario@exemplo.com", "senha": "minhasenha123"}'
    """
    # Buscar usuário pelo email (independentemente do status ativo/inativo)
    usuario = crud_usuario.get_usuario_by_email_all_status(db, email=login_data.email)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar se o usuário está ativo
    if not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo. Por favor, contate o suporte.",
        )
    
    # Verifica senha: usa o hash armazenado
    if not verify_password(login_data.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": usuario.email}, expires_delta=access_token_expires
    )
    
    # Define o cookie HttpOnly para segurança em rotas HTML
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False  # Alterar para True em produção com HTTPS
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

from backend.app.schemas.usuario import UsuarioCreate
import logging
logger = logging.getLogger(__name__)

@router.post("/registro", response_model=schemas_auth.Token)
async def registro(
    usuario_in: schemas_auth.RegistroUsuario,
    db: Session = Depends(get_db)
) -> Any:
    """
    Registra um novo usuário ou reativa/atualiza um usuário inativo e retorna um token de acesso.
    """
    # 1. Tenta encontrar qualquer usuário (ativo ou inativo) com o email fornecido
    existing_usuario = crud_usuario.get_usuario_by_email_all_status(db, email=usuario_in.email)

    if existing_usuario:
        if existing_usuario.ativo:
            # Se o usuário existe e está ativo, não permite novo registro
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )
        else:
            # Se o usuário existe mas está inativo, reativa e atualiza
            existing_usuario.ativo = True
            existing_usuario.nome = usuario_in.nome
            existing_usuario.endereco = usuario_in.endereco
            existing_usuario.set_senha(usuario_in.senha) # Atualiza a senha
            
            db.add(existing_usuario)
            db.commit()
            db.refresh(existing_usuario)
            usuario = existing_usuario
    else:
        # Se não encontrou nenhum usuário, cria um novo
        usuario_create = UsuarioCreate(
            nome=usuario_in.nome,
            email=usuario_in.email,
            endereco=usuario_in.endereco,
            senha=usuario_in.senha
        )
        usuario = crud_usuario.create_usuario(db, usuario=usuario_create)
    
    # Enviar e-mail de confirmação de cadastro
    try:
        from backend.app.utils.email_yagmail import send_confirmacao_cadastro_yagmail
        email_enviado = send_confirmacao_cadastro_yagmail(
            email_to=usuario.email,
            nome_usuario=usuario.nome,
            endereco=usuario.endereco
        )
        
        if not email_enviado:
            logger.warning(f"Falha ao enviar e-mail de confirmação para {usuario.email}")
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail de confirmação para {usuario.email}: {str(e)}")
    
    # Gera o token de acesso
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": usuario.email}, expires_delta=access_token_expires
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
        data={"sub": usuario.email, "type": "password_reset"},
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
    
    usuario = crud_usuario.get_usuario_by_email(db, email=token_data.email)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Atualiza a senha
    hashed_password = get_password_hash(reset_data.nova_senha)
    crud_usuario.update_password(db, usuario=usuario, new_password=hashed_password)
    
    return {"message": "Senha atualizada com sucesso"}

@router.post("/logout")
async def logout(response: Response) -> Any:
    """
    Realiza o logout do usuário removendo o cookie de autenticação.
    """
    response.delete_cookie(key="access_token")
    return {"message": "Logout realizado com sucesso"}