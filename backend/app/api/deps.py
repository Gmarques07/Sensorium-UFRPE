from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import SessionLocal
from app import crud, schemas
from app.models import Usuario, Admin

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

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
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        cpf: str = payload.get("sub")
        if cpf is None:
            raise credentials_exception
        token_data = schemas.auth.TokenData(cpf=cpf)
    except JWTError:
        raise credentials_exception
    user = crud.usuario.get_by_cpf(db, cpf=token_data.cpf)
    if user is None:
        raise credentials_exception
    return user

def get_current_admin(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> Admin:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate admin credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        cpf: str = payload.get("sub")
        if cpf is None:
            raise credentials_exception
        token_data = schemas.auth.TokenData(cpf=cpf)
    except JWTError:
        raise credentials_exception
    admin = crud.admin.get_by_cpf(db, cpf=token_data.cpf)
    if admin is None:
        raise credentials_exception
    return admin