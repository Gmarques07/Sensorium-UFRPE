from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.cisterna import PhNivel, NivelAgua
from app.schemas.cisterna import PhNivelCreate, NivelAguaCreate

def criar_ph_nivel(db: Session, ph: PhNivelCreate) -> PhNivel:
    db_ph = PhNivel(ph=ph.ph)
    db.add(db_ph)
    db.commit()
    db.refresh(db_ph)
    return db_ph

def obter_ultimo_ph(db: Session) -> Optional[PhNivel]:
    return db.query(PhNivel).order_by(desc(PhNivel.data)).first()

def obter_historico_ph(db: Session, limit: int = 10) -> List[PhNivel]:
    return db.query(PhNivel).order_by(desc(PhNivel.data)).limit(limit).all()

def criar_nivel_agua(db: Session, nivel: NivelAguaCreate) -> NivelAgua:
    db_nivel = NivelAgua(
        boia=nivel.boia,
        status=NivelAgua.calcular_status(nivel.boia)
    )
    db.add(db_nivel)
    db.commit()
    db.refresh(db_nivel)
    return db_nivel

def obter_ultimo_nivel(db: Session) -> Optional[NivelAgua]:
    return db.query(NivelAgua).order_by(desc(NivelAgua.data)).first()

def obter_historico_nivel(db: Session, limit: int = 10) -> List[NivelAgua]:
    return db.query(NivelAgua).order_by(desc(NivelAgua.data)).limit(limit).all()

def obter_dados_cisterna(db: Session, limite_historico: int = 10) -> Tuple[Optional[PhNivel], List[PhNivel], Optional[NivelAgua], List[NivelAgua]]:
    ph_atual = obter_ultimo_ph(db)
    historico_ph = obter_historico_ph(db, limite_historico)
    nivel_atual = obter_ultimo_nivel(db)
    historico_nivel = obter_historico_nivel(db, limite_historico)
    
    return ph_atual, historico_ph, nivel_atual, historico_nivel
