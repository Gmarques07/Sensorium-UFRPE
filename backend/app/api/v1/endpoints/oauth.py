from typing import Any, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Request, Query
from fastapi.responses import RedirectResponse, HTMLResponse
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
    if not settings.GOOGLE_CLIENT_ID or not settings.google_redirect_uri:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Credenciais do Google não configuradas corretamente. Verifique o arquivo .env."
        )

    google_auth_url = "https://accounts.google.com/o/oauth2/auth"

    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.google_redirect_uri,
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
    code: Optional[str] = Query(None), # Make code optional
    error: Optional[str] = Query(None), # Add error parameter
    db: Session = Depends(get_db)
):
    """
    Callback para processar a resposta do Google OAuth e redirecionar adequadamente
    """
    # Early exit for cancellation/errors
    if code is None or error is not None:
        # User cancelled or an error occurred during Google OAuth
        print(f"Google OAuth cancelled or error: code={code}, error={error}") # For debugging
        # Determine message based on error type
        message_type = "google_error" # Default generic error
        if code is None: # If 'code' is missing, it's likely a user-initiated cancellation or an early failure
            message_type = "google_cancelled" # Treat missing code as a cancellation
        elif error == "access_denied": # If 'code' is present but 'access_denied' is also there, it's an access denial from Google
            message_type = "google_access_denied"
        elif error is not None: # Any other specific error from Google
            message_type = "google_error"

        redirect_url = f"{settings.BASE_URL}/login?message={message_type}"
        return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)

    try:
        # Verificar se as credenciais do Google estão configuradas
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Chave secreta do Google não configurada. Verifique o arquivo .env e adicione GOOGLE_CLIENT_SECRET."
            )

        # Usar o redirect_uri baseado no ambiente
        redirect_uri = settings.google_redirect_uri

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
        access_token_google = token_json.get("access_token") # Renomeado para evitar conflito

        if not access_token_google:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de acesso não encontrado na resposta do Google"
            )

        # Obter informações do usuário do Google
        user_info_response = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token_google}"}
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

        # Determinar se é novo cadastro ou login existente
        usuario_existente = crud_usuario.get_usuario_by_email_all_status(db, email=google_email)
        is_new_user = usuario_existente is None

        if not usuario_existente:
            # Criar novo usuário OAuth
            usuario_in = UsuarioCreate(
                nome=google_name,
                email=google_email,
                endereco="",  # Pode ser preenchido posteriormente
                senha=""  # Não é necessário para login OAuth
            )
            usuario = crud_usuario.create_usuario_oauth(db, usuario=usuario_in)
            print(f"[OAuth] Novo usuário OAuth criado: {google_email} ({google_name})")
        else:
            # Usuário já existe, atualiza informações conforme necessário
            usuario_existente.ativo = True  # Reativar se estiver inativo
            if usuario_existente.nome != google_name:
                usuario_existente.nome = google_name
            db.commit()
            db.refresh(usuario_existente)
            usuario = usuario_existente
            print(f"[OAuth] Login OAuth existente: {google_email} ({google_name}) - ID: {usuario.id}")

        # Criar token de acesso JWT
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": usuario.email}, expires_delta=access_token_expires
        )

        # Criar uma resposta HTML temporária com redirecionamento via JavaScript
        # Isso permite que o cookie seja processado antes do redirecionamento
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Autenticação Google</title>
        </head>
        <body>
            <script>
                // Definir o cookie de acesso no JavaScript também como fallback
                document.cookie = "access_token=Bearer {access_token}; path=/; max-age={settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60}; samesite=lax; {(settings.ENVIRONMENT == 'production') and 'secure;' or ''}";

                // Agora redirecionar para o dashboard
                window.location.href = "/dashboard";
            </script>
        </body>
        </html>
        """

        response = HTMLResponse(content=html_content)

        # Definir o cookie também na resposta para garantir compatibilidade
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax",
            secure=(settings.ENVIRONMENT == "production"),  # Usar secure=True em produção com HTTPS
            path="/"
        )

        return response

    except HTTPException:
        # Re-lançar HTTPExceptions para manter os códigos de erro apropriados
        raise
    except Exception as e:
        # Log mais detalhado para depuração
        print(f"Erro no callback do Google OAuth: {str(e)}")
        print(f"Request URL: {request.url}")
        import traceback
        traceback.print_exc()

        # Verificar se é um erro de chave duplicada
        error_msg = str(e).lower()
        if "duplicate entry" in error_msg and "email" in error_msg:
            # É um erro de e-mail duplicado - o usuário deve existir, então vamos buscar e usar
            try:
                print(f"[OAuth] Erro de duplicidade detectado para o e-mail: {google_email}")
                usuario_existente = crud_usuario.get_usuario_by_email_all_status(db, email=google_email)
                if usuario_existente:
                    print(f"[OAuth] Usuário duplicado encontrado, usando existente: {google_email} - ID: {usuario_existente.id}")
                    # Usuário já existe, vamos apenas gerar o token
                    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
                    access_token = create_access_token(
                        data={"sub": usuario_existente.email}, expires_delta=access_token_expires
                    )

                    # Criar uma resposta HTML temporária com redirecionamento via JavaScript
                    # Isso permite que o cookie seja processado antes do redirecionamento
                    html_content = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Autenticação Google</title>
                    </head>
                    <body>
                        <script>
                            // Definir o cookie de acesso no JavaScript também como fallback
                            document.cookie = "access_token=Bearer {access_token}; path=/; max-age={settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60}; samesite=lax; {(settings.ENVIRONMENT == 'production') and 'secure;' or ''}";

                            // Agora redirecionar para o dashboard
                            window.location.href = "/dashboard";
                        </script>
                    </body>
                    </html>
                    """

                    response = HTMLResponse(content=html_content)

                    # Definir o cookie também na resposta para garantir compatibilidade
                    response.set_cookie(
                        key="access_token",
                        value=f"Bearer {access_token}",
                        httponly=True,
                        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                        samesite="lax",
                        secure=(settings.ENVIRONMENT == "production"),  # Usar secure=True em produção com HTTPS
                        path="/"
                    )

                    return response
                else:
                    print(f"[OAuth] Usuário não encontrado mesmo após erro de duplicidade: {google_email}")
            except Exception as inner_e:
                print(f"[OAuth] Erro ao tentar recuperar usuário existente após duplicidade: {inner_e}")
                pass  # Se falhar, continuar com o erro original

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno durante o processo de autenticação do Google: {str(e)}"
        )
