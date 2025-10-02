from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.app.models import Local, Leitura, PhNivel, BoiaNivel
from backend.app.schemas import LocalCreate, PhNivelCreate, BoiaNivelCreate

def criar_local(db: Session, local: LocalCreate) -> Local:
    db_local = Local(
        nome=local.nome,
        tipo=local.tipo,
        descricao=local.descricao
    )
    db.add(db_local)
    db.commit()
    db.refresh(db_local)
    return db_local

def criar_ph_nivel(db: Session, ph: PhNivelCreate, local_id: int) -> PhNivel:
    leitura = Leitura(local_id=local_id, sensor_tipo='PH')
    db.add(leitura)
    db.commit()
    db.refresh(leitura)

    db_ph = PhNivel(leitura_id=leitura.id, ph=ph.ph)
    db.add(db_ph)
    db.commit()
    db.refresh(db_ph)
    return db_ph

def obter_ultimo_ph(db: Session, local_id: int) -> Optional[PhNivel]:
    return db.query(PhNivel).join(Leitura).filter(Leitura.local_id == local_id).order_by(desc(Leitura.data)).first()

def obter_historico_ph(db: Session, local_id: int, limit: int = 10) -> List[PhNivel]:
    return db.query(PhNivel).join(Leitura).filter(Leitura.local_id == local_id).order_by(desc(Leitura.data)).limit(limit).all()

def criar_boia_nivel(db: Session, boia: BoiaNivelCreate, local_id: int) -> BoiaNivel:
    leitura = Leitura(local_id=local_id, sensor_tipo='BOIA')
    db.add(leitura)
    db.commit()
    db.refresh(leitura)

    db_boia = BoiaNivel(leitura_id=leitura.id, valor=boia.valor, status=boia.status)
    db.add(db_boia)
    db.commit()
    db.refresh(db_boia)
    return db_boia

def obter_ultimo_nivel_boia(db: Session, local_id: int) -> Optional[BoiaNivel]:
    return db.query(BoiaNivel).join(Leitura).filter(Leitura.local_id == local_id).order_by(desc(Leitura.data)).first()

def obter_historico_nivel_boia(db: Session, local_id: int, limit: int = 10) -> List[BoiaNivel]:
    return db.query(BoiaNivel).join(Leitura).filter(Leitura.local_id == local_id).order_by(desc(Leitura.data)).limit(limit).all()

def obter_dados_cisterna(db: Session, local_id: int, limite_historico: int = 10) -> Tuple[Optional[PhNivel], List[PhNivel], Optional[BoiaNivel], List[BoiaNivel]]:
    ph_atual = obter_ultimo_ph(db, local_id)
    historico_ph = obter_historico_ph(db, local_id, limite_historico)
    nivel_atual = obter_ultimo_nivel_boia(db, local_id)
    historico_nivel = obter_historico_nivel_boia(db, local_id, limite_historico)
    
    return ph_atual, historico_ph, nivel_atual, historico_nivel
