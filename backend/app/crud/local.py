from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.app.models import Local, Leitura, PhNivel, BoiaNivel
from backend.app.schemas import LocalCreate, PhNivelCreate, BoiaNivelCreate
from backend.app.utils.api_key_generator import generate_unique_api_key

def criar_local(db: Session, local: LocalCreate) -> Local:
    # Generate a unique API key for the sensor
    api_key = generate_unique_api_key(db)

    db_local = Local(
        nome=local.nome,
        tipo=local.tipo,
        descricao=local.descricao,
        chave_api=api_key
    )
    db.add(db_local)
    db.commit()
    db.refresh(db_local)
    return db_local

def criar_local_com_chave(db: Session, local: LocalCreate, chave_api: str = None) -> Local:
    """Cria um local com uma chave de API específica (usado para o registro do sensor pelo usuário)"""
    if not chave_api:
        chave_api = generate_unique_api_key(db)

    db_local = Local(
        nome=local.nome,
        tipo=local.tipo,
        descricao=local.descricao,
        chave_api=chave_api
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

def deletar_local(db: Session, local_id: int) -> bool:
    """Deleta um local pelo ID e todas as suas associações e leituras associadas."""
    from backend.app.models.notificacao import Notificacao
    from backend.app.models.regra_alerta import RegraAlerta
    from backend.app.models.leitura import Leitura, PhNivel, BoiaNivel, UmidadeNivel

    local = db.query(Local).filter(Local.id == local_id).first()
    if local:
        # Primeiro, obter os IDs das leituras associadas a este local
        leitura_ids = db.query(Leitura.id).filter(Leitura.local_id == local_id).all()
        leitura_ids = [l[0] for l in leitura_ids]  # Extrair os IDs da tupla

        if leitura_ids:
            # Remover registros dependentes primeiro
            db.query(PhNivel).filter(PhNivel.leitura_id.in_(leitura_ids)).delete(synchronize_session=False)
            db.query(BoiaNivel).filter(BoiaNivel.leitura_id.in_(leitura_ids)).delete(synchronize_session=False)
            db.query(UmidadeNivel).filter(UmidadeNivel.leitura_id.in_(leitura_ids)).delete(synchronize_session=False)

        # Em seguida, remover as leituras
        db.query(Leitura).filter(Leitura.local_id == local_id).delete(synchronize_session=False)

        # Remover todas as regras de alerta associadas a este local
        db.query(RegraAlerta).filter(RegraAlerta.local_id == local_id).delete(synchronize_session=False)

        # Remover todas as notificações associadas a este local
        db.query(Notificacao).filter(Notificacao.local_id == local_id).delete(synchronize_session=False)

        # Remover o local em si
        db.delete(local)
        db.commit()
        return True
    return False
