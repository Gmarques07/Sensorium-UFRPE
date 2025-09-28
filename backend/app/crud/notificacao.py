from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from ..models.notificacao import Notificacao, NotificacaoAdmin
from ..schemas.notificacao import NotificacaoCreate, NotificacaoUpdate

def get_notificacao(db: Session, notificacao_id: int) -> Optional[Notificacao]:
    return db.query(Notificacao).filter(Notificacao.id == notificacao_id).first()

def get_notificacoes_usuario(db: Session, email_usuario: str, skip: int = 0, limit: int = 10) -> List[Notificacao]:
    return (
        db.query(Notificacao)
        .filter(Notificacao.email_usuario == email_usuario)
        .order_by(Notificacao.data_criacao.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_notificacoes_por_local(db: Session, local_id: int, skip: int = 0, limit: int = 10) -> List[Notificacao]:
    return (
        db.query(Notificacao)
        .filter(Notificacao.local_id == local_id)
        .order_by(Notificacao.data_criacao.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_notificacao(db: Session, notificacao: NotificacaoCreate) -> Notificacao:
    db_notificacao = Notificacao(
        mensagem=notificacao.mensagem,
        local_id=notificacao.local_id,
        email_usuario=notificacao.email_usuario,
        tipo=notificacao.tipo
    )
    db.add(db_notificacao)
    db.commit()
    db.refresh(db_notificacao)
    return db_notificacao

def update_notificacao(db: Session, notificacao_id: int, notificacao: NotificacaoUpdate) -> Optional[Notificacao]:
    db_notificacao = get_notificacao(db, notificacao_id)
    if db_notificacao is None:
        return None
    
    update_data = notificacao.model_dump(exclude_unset=True)
    
    # Se estiver marcando como lida, adiciona a data de leitura
    if update_data.get("lida"):
        update_data["data_leitura"] = datetime.now(timezone.utc)
    
    for key, value in update_data.items():
        setattr(db_notificacao, key, value)
    
    db.commit()
    db.refresh(db_notificacao)
    return db_notificacao

def delete_notificacao(db: Session, notificacao_id: int) -> bool:
    db_notificacao = get_notificacao(db, notificacao_id)
    if db_notificacao is None:
        return False
    
    db.delete(db_notificacao)
    db.commit()
    return True

# Funções para NotificacoesAdmin

def get_notificacao_admin(db: Session, notificacao_id: int) -> Optional[NotificacaoAdmin]:
    return db.query(NotificacaoAdmin).filter(NotificacaoAdmin.id == notificacao_id).first()

def get_notificacoes_admin(db: Session, apenas_nao_lidas: bool = False, skip: int = 0, limit: int = 10) -> List[NotificacaoAdmin]:
    query = db.query(NotificacaoAdmin)
    if apenas_nao_lidas:
        query = query.filter(NotificacaoAdmin.lida == False)
    return query.order_by(NotificacaoAdmin.data_criacao.desc()).offset(skip).limit(limit).all()

def create_notificacao_admin(db: Session, tipo: str, titulo: str, mensagem: str) -> NotificacaoAdmin:
    db_notificacao = NotificacaoAdmin(
        tipo=tipo,
        titulo=titulo,
        mensagem=mensagem
    )
    db.add(db_notificacao)
    db.commit()
    db.refresh(db_notificacao)
    return db_notificacao

def marcar_notificacao_admin_como_lida(db: Session, notificacao_id: int) -> Optional[NotificacaoAdmin]:
    db_notificacao = get_notificacao_admin(db, notificacao_id)
    if db_notificacao is None:
        return None
    
    db_notificacao.lida = True
    db_notificacao.data_leitura = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_notificacao)
    return db_notificacao
