from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Cookie, Header
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.db.session import SessionLocal
from backend.app import crud, schemas
from backend.app.models.usuario import Usuario
from backend.app.models.admin import Admin
from backend.app.models.local import Local

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception
        
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.auth.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = crud.usuario.get_usuario_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    if not user.ativo:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

def get_current_admin(
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme),
    admin_access_token: Optional[str] = Cookie(None)
) -> Admin:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate admin credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verificar se o token foi fornecido via header ou cookie
    if not token and admin_access_token:
        token = admin_access_token.replace("Bearer ", "")

    if not token:
        raise credentials_exception
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if email is None or token_type != "admin":
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    admin = db.query(Admin).filter(Admin.email == email).first()
    if admin is None:
        raise credentials_exception
    return admin

def get_current_admin_from_cookie(
    db: Session = Depends(get_db), 
    admin_access_token: Optional[str] = Cookie(None)
) -> Admin:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate admin credentials from cookie",
    )
    
    if not admin_access_token:
        raise credentials_exception
        
    token = admin_access_token.replace("Bearer ", "")
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if email is None or token_type != "admin":
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    admin = db.query(Admin).filter(Admin.email == email).first()
    if admin is None:
        raise credentials_exception
    return admin

def get_current_user_from_cookie(
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(None)
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials from cookie",
    )

    if not access_token:
        raise credentials_exception

    token = access_token.replace("Bearer ", "")

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud.usuario.get_usuario_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    if not user.ativo:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

def get_sensor_by_api_key_optional(
    db: Session = Depends(get_db),
    api_key: str = Header(None, alias="X-API-Key")
) -> Local:
    """
    Optional dependency to validate sensor API key from header
    Returns None if no API key is provided or if invalid
    """
    if not api_key:
        return None

    # Find the local with the given API key
    local = db.query(Local).filter(Local.chave_api == api_key).first()

    if local is None:
        return None

    return local

def get_sensor_by_api_key_strict(
    db: Session = Depends(get_db),
    api_key: str = Header(None, alias="X-API-Key")
) -> Local:
    """
    Strict dependency to validate sensor API key from header
    Raises HTTP 401 if API key is provided but invalid
    """
    if not api_key:
        # If no API key is provided, return None to allow other auth methods
        return None

    # Find the local with the given API key
    local = db.query(Local).filter(Local.chave_api == api_key).first()

    if local is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "API-Key"},
        )

    return local

def get_current_user_optional(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> Optional[Usuario]:
    """
    Optional dependency to get current user from token
    Returns None if no token is provided or if invalid
    """
    try:
        return get_current_user(db, token)
    except HTTPException:
        # If token is invalid or not provided, return None
        return None

def get_authenticated_sensor_or_user(
    db: Session = Depends(get_db),
    api_key: str = Header(None, alias="X-API-Key"),
    token: str = Depends(oauth2_scheme)
) -> tuple[Optional[Local], Optional[Usuario]]:
    """
    Authentication dependency that accepts either API key or user token
    Returns tuple of (sensor, user) - at least one must be valid
    """
    sensor = None
    user = None

    # Try API key authentication first
    if api_key:
        sensor = db.query(Local).filter(Local.chave_api == api_key).first()
        if sensor is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "API-Key"},
            )

    # Try user token authentication if no API key was provided or if we want dual auth
    if not api_key and token:
        user = get_current_user(db, token)
    elif api_key and token:
        # If both are provided, validate user token as well
        user = get_current_user(db, token)

    # At least one form of authentication must be valid
    if not sensor and not user:
        raise HTTPException(
            status_code=401,
            detail="Either API key or user token is required for authentication"
        )

    return sensor, user