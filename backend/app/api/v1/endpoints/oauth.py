from typing import Any
from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from urllib.parse import urlencode
import requests
from backend.app.api.deps import get_db
from backend.app.core.config import settings
from backend.app.crud import usuario as crud_usuario
from backend.app.schemas.usuario import UsuarioCreate
from backend.app.schemas.auth import OAuthLoginResponse, OAuthUserResponse
from backend.app.core.security import create_access_token
from datetime import timedelta

router = APIRouter()

@router.get("/google/login")
async def google_login():
    """
    Inicia o processo de autenticação com o Google
    """
    # Verificar se as credenciais do Google estão configuradas
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_REDIRECT_URI:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Credenciais do Google não configuradas corretamente. Verifique o arquivo .env."
        )
    
    google_auth_url = "https://accounts.google.com/o/oauth2/auth"
    
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    
    auth_url = f"{google_auth_url}?{urlencode(params)}"
    return RedirectResponse(url=auth_url)

@router.get("/google/callback")
async def google_callback(
    request: Request,
    code: str, 
    db: Session = Depends(get_db)
):
    """
    Callback para processar a resposta do Google OAuth e redirecionar adequadamente
    """
    try:
        # Verificar se as credenciais do Google estão configuradas
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Chave secreta do Google não configurada. Verifique o arquivo .env e adicione GOOGLE_CLIENT_SECRET."
            )
        
        # Verificar e corrigir a porta no redirect_uri se necessário
        redirect_uri = settings.GOOGLE_REDIRECT_URI
        # Assegurar que estamos usando a porta correta (8002)
        if "localhost:8003" in redirect_uri:
            redirect_uri = redirect_uri.replace("localhost:8003", "localhost:8002")
        
        # Trocar o código de autorização por um token de acesso
        token_url = "https://oauth2.googleapis.com/token"
        
        token_data = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }
        
        token_response = requests.post(token_url, data=token_data)
        
        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro ao obter token de acesso do Google. Status: {token_response.status_code}, Resposta: {token_response.text}"
            )
        
        token_json = token_response.json()
        access_token = token_json.get("access_token")
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de acesso não encontrado na resposta do Google"
            )
        
        # Obter informações do usuário do Google
        user_info_response = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if user_info_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro ao obter informações do usuário do Google. Status: {user_info_response.status_code}"
            )
        
        user_info = user_info_response.json()
        
        # Extrair informações do usuário
        google_email = user_info.get("email")
        google_name = user_info.get("name", "")
        google_id = user_info.get("id", "")
        
        if not google_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email não encontrado nas informações do Google"
            )
        
        # Verificar se o usuário já existe no banco de dados
        usuario = crud_usuario.get_usuario_by_email(db, email=google_email)
        
        # Determinar se é novo cadastro ou login existente
        is_new_user = usuario is None
        
        if not usuario:
            # Criar novo usuário OAuth
            usuario_in = UsuarioCreate(
                nome=google_name,
                email=google_email,
                endereco="",  # Pode ser preenchido posteriormente
                senha=""  # Não é necessário para login OAuth
            )
            usuario = crud_usuario.create_usuario_oauth(db, usuario=usuario_in)
        else:
            # Atualizar informações do usuário existente se necessário
            if usuario.nome != google_name:
                usuario.nome = google_name
                db.commit()
                db.refresh(usuario)
        
        # Criar token de acesso JWT
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": usuario.email}, expires_delta=access_token_expires
        )
        
        # Determinar para onde redirecionar
        if is_new_user:
            # Se for um novo usuário (cadastro), redirecionar para login
            redirect_url = f"https://sensoriumtech.online/login_usuario.html?token={access_token}"
        else:
            # Se for login de usuário existente, redirecionar para dashboard
            redirect_url = f"https://sensoriumtech.online/dashboard_usuario.html?token={access_token}"
        
        # Retornar redirecionamento
        return RedirectResponse(url=redirect_url)
        
    except HTTPException:
        # Re-lançar HTTPExceptions para manter os códigos de erro apropriados
        raise
    except Exception as e:
        # Log mais detalhado para depuração
        print(f"Erro no callback do Google OAuth: {str(e)}")
        print(f"Request URL: {request.url}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno durante o processo de autenticação do Google: {str(e)}"
        )