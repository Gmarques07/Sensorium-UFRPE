from typing import Optional, List
from sqlalchemy.orm import Session
from backend.app.models.usuario import Usuario
from backend.app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

def get_usuario(db: Session, usuario_id: int) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()

def get_usuario_by_email(db: Session, email: str) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.email == email, Usuario.ativo == True).first()

def get_usuario_by_email_all_status(db: Session, email: str) -> Optional[Usuario]:
    """Obtém usuário por email, independentemente do status ativo/inativo"""
    return db.query(Usuario).filter(Usuario.email == email).first()

def get_usuarios(db: Session, skip: int = 0, limit: int = 100) -> List[Usuario]:
    return db.query(Usuario).offset(skip).limit(limit).all()

def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[Usuario]:
    return db.query(Usuario).order_by(Usuario.created_at.desc()).offset(skip).limit(limit).all()

def create_usuario(db: Session, usuario: UsuarioCreate) -> Usuario:
    db_usuario = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        endereco=usuario.endereco
    )
    db_usuario.set_senha(usuario.senha)
    
    try:
        db.add(db_usuario)
        db.commit()
        db.refresh(db_usuario)
        return db_usuario
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Já existe uma conta com este email.",
        )


def create_usuario_oauth(db: Session, usuario: UsuarioCreate) -> Usuario:
    """
    Cria um usuário OAuth (sem senha, pois a autenticação é feita pelo provedor OAuth)
    """
    # Verificar novamente se o usuário já existe para evitar problemas de concorrência
    existing_usuario = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if existing_usuario:
        print(f"[OAuth] Usuário OAuth já existe para o email: {usuario.email}, reativando/atualizando")
        # Se já existe, apenas reativar se estiver inativo
        if not existing_usuario.ativo:
            existing_usuario.ativo = True
            existing_usuario.nome = usuario.nome
            db.commit()
            db.refresh(existing_usuario)
        return existing_usuario

    print(f"[OAuth] Criando novo usuário OAuth para o email: {usuario.email}")
    db_usuario = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        endereco=usuario.endereco or ""
    )
    # Não definimos senha para usuários OAuth, mas precisamos de um hash
    # Vamos usar uma senha aleatória ou deixar vazio
    # Como não usaremos a senha para login OAuth, podemos gerar uma senha aleatória
    import secrets
    import string
    random_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    db_usuario.set_senha(random_password)  # A senha é definida mas não será usada

    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def update_usuario(
    db: Session, 
    usuario: Usuario,
    usuario_in: UsuarioUpdate
) -> Usuario:
    update_data = usuario_in.model_dump(exclude_unset=True)
    
    if "senha" in update_data:
        usuario.set_senha(update_data["senha"])
        del update_data["senha"]
    
    for field, value in update_data.items():
        setattr(usuario, field, value)

    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario

def update_password(db: Session, usuario: Usuario, new_password: str) -> Usuario:
    """Atualiza a senha do usuário"""
    usuario.senha_hash = new_password  # A senha já deve vir hasheada
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario

def deactivate_usuario(db: Session, usuario: Usuario) -> Usuario:
    """
    Marca um usuário como inativo em vez de deletá-lo permanentemente.
    """
    usuario.ativo = False
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario

def delete_usuario(db: Session, usuario: Usuario) -> bool:
    """
    Mantém compatibilidade com interfaces antigas: realiza soft-delete usando
    deactivate_usuario e retorna True/False para sucesso.
    """
    try:
        deactivate_usuario(db, usuario)
        return True
    except Exception:
        db.rollback()
        return False