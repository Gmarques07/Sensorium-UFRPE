from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate

def get_usuario(db: Session, usuario_id: int) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()

def get_usuario_by_cpf(db: Session, cpf: str) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.cpf == cpf, Usuario.ativo == True).first()

def get_usuario_by_email(db: Session, email: str) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.email == email, Usuario.ativo == True).first()

def get_usuarios(db: Session, skip: int = 0, limit: int = 100) -> List[Usuario]:
    return db.query(Usuario).offset(skip).limit(limit).all()

def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[Usuario]:
    return db.query(Usuario).offset(skip).limit(limit).all()

def create_usuario(db: Session, usuario: UsuarioCreate) -> Usuario:
    db_usuario = Usuario(
        cpf=usuario.cpf,
        nome=usuario.nome,
        email=usuario.email,
        endereco=usuario.endereco
    )
    db_usuario.set_senha(usuario.senha)
    
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def update_usuario(
    db: Session, 
    usuario: Usuario,
    usuario_in: UsuarioUpdate
) -> Usuario:
    update_data = usuario_in.dict(exclude_unset=True)
    
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

# def delete_usuario(db: Session, usuario: Usuario) -> bool:
#     """
#     Deleta um usuário permanentemente do banco de dados.
#     """
#     try:
#         db.delete(usuario)
#         db.commit()
#         return True
#     except Exception:
#         db.rollback()
#         return False
