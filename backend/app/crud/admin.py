from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..models.admin import Configuracao, Admin
from ..schemas.admin import ConfiguracaoCreate, ConfiguracaoUpdate

def get_configuracao(db: Session, chave: str) -> Optional[Configuracao]:
    return db.query(Configuracao).filter(Configuracao.chave == chave).first()

def get_by_cpf(db: Session, cpf: str) -> Optional[Admin]:
    return db.query(Admin).filter(Admin.cpf == cpf).first()

def get_all_configuracoes(db: Session, skip: int = 0, limit: int = 100) -> List[Configuracao]:
    return db.query(Configuracao).offset(skip).limit(limit).all()

def create_configuracao(db: Session, config: ConfiguracaoCreate) -> Configuracao:
    db_config = Configuracao(**config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

def update_configuracao(
    db: Session, 
    chave: str, 
    config_in: ConfiguracaoUpdate
) -> Optional[Configuracao]:
    db_config = get_configuracao(db, chave)
    if not db_config:
        return None
    
    update_data = config_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_config, field, value)
    
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

def delete_configuracao(db: Session, chave: str) -> bool:
    db_config = get_configuracao(db, chave)
    if not db_config:
        return False
    
    db.delete(db_config)
    db.commit()
    return True

def get_dashboard_stats(db: Session) -> Dict[str, Any]:
    """
    Obtém estatísticas para o dashboard administrativo
    """
    # Total de usuários
    total_usuarios = db.execute(text("SELECT COUNT(*) FROM usuarios")).scalar()
    
    # Usuários ativos (com login nos últimos 30 dias)
    usuarios_ativos = db.execute(
        text("""SELECT COUNT(DISTINCT user_id) 
           FROM user_sessions 
           WHERE last_activity >= DATE_SUB(NOW(), INTERVAL 30 DAY)""")
    ).scalar()
    
    # Total de pedidos
    total_pedidos = db.execute(text("SELECT COUNT(*) FROM pedidos")).scalar()
    
    # Total de notificações
    total_notificacoes = db.execute(text("SELECT COUNT(*) FROM notificacoes")).scalar()
    
    # Dados das cisternas
    dados_cisterna = db.execute(
        text("""SELECT 
            COUNT(*) as total_leituras,
            AVG(nivel) as nivel_medio,
            AVG(ph) as ph_medio
           FROM leituras_cisterna 
           WHERE data_leitura >= DATE_SUB(NOW(), INTERVAL 24 HOUR)""")
    ).first()
    
    return {
        "total_usuarios": total_usuarios,
        "usuarios_ativos": usuarios_ativos,
        "total_pedidos": total_pedidos,
        "total_notificacoes": total_notificacoes,
        "dados_cisterna": dict(dados_cisterna) if dados_cisterna else {}
    }
