from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.regra_alerta import RegraAlerta
from ..schemas.regra_alerta import RegraAlertaCreate, RegraAlertaUpdate


def get_regra_alerta(db: Session, regra_id: int) -> Optional[RegraAlerta]:
    return db.query(RegraAlerta).filter(RegraAlerta.id == regra_id).first()


def get_regras_alerta_por_usuario(db: Session, usuario_email: str, skip: int = 0, limit: int = 100) -> List[RegraAlerta]:
    return (
        db.query(RegraAlerta)
        .filter(RegraAlerta.usuario_email == usuario_email)
        .order_by(RegraAlerta.data_criacao.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_regras_alerta_por_local(db: Session, local_id: int, skip: int = 0, limit: int = 100) -> List[RegraAlerta]:
    return (
        db.query(RegraAlerta)
        .filter(RegraAlerta.local_id == local_id)
        .order_by(RegraAlerta.data_criacao.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_regras_alerta_por_usuario_e_local(db: Session, usuario_email: str, local_id: int) -> List[RegraAlerta]:
    return (
        db.query(RegraAlerta)
        .filter(RegraAlerta.usuario_email == usuario_email)
        .filter(RegraAlerta.local_id == local_id)
        .filter(RegraAlerta.ativa == True)
        .all()
    )


def create_regra_alerta(db: Session, regra: RegraAlertaCreate) -> RegraAlerta:
    db_regra = RegraAlerta(**regra.model_dump())
    db.add(db_regra)
    db.commit()
    db.refresh(db_regra)
    return db_regra


def update_regra_alerta(db: Session, regra_id: int, regra: RegraAlertaUpdate) -> Optional[RegraAlerta]:
    db_regra = get_regra_alerta(db, regra_id)
    if not db_regra:
        return None

    update_data = regra.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_regra, key, value)
    
    db.commit()
    db.refresh(db_regra)
    return db_regra


def delete_regra_alerta(db: Session, regra_id: int) -> bool:
    db_regra = get_regra_alerta(db, regra_id)
    if not db_regra:
        return False

    db.delete(db_regra)
    db.commit()
    return True


def get_regras_alerta_violadas(db: Session, local_id: int, leitura_atual: dict) -> List[RegraAlerta]:
    """
    Retorna as regras de alerta que foram violadas com base nos dados de leitura atuais.
    """
    # Obter todas as regras ativas para este local
    regras_ativas = (
        db.query(RegraAlerta)
        .filter(RegraAlerta.local_id == local_id)
        .filter(RegraAlerta.ativa == True)
        .all()
    )
    
    regras_violadas = []
    for regra in regras_ativas:
        campo_valor = leitura_atual.get(regra.campo_sensor)
        if campo_valor is not None:
            # Avaliar a condição da regra
            if regra.operador == '>' and campo_valor > regra.valor_limite:
                regras_violadas.append(regra)
            elif regra.operador == '<' and campo_valor < regra.valor_limite:
                regras_violadas.append(regra)
            elif regra.operador == '>=' and campo_valor >= regra.valor_limite:
                regras_violadas.append(regra)
            elif regra.operador == '<=' and campo_valor <= regra.valor_limite:
                regras_violadas.append(regra)
            elif regra.operador == '==' and campo_valor == regra.valor_limite:
                regras_violadas.append(regra)
            elif regra.operador == '!=' and campo_valor != regra.valor_limite:
                regras_violadas.append(regra)
    
    return regras_violadas