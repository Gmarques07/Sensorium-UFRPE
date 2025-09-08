from sqlalchemy.orm import Session
from sqlalchemy import and_
from backend.app.models.usuario_sensor import UsuarioSensor
from backend.app.schemas.usuario_sensor import UsuarioSensorCreate, UsuarioSensorUpdate

def get_usuario_sensor(db: Session, usuario_id: int, sensor_id: int) -> UsuarioSensor:
    """Obtém um relacionamento específico entre usuário e sensor."""
    return db.query(UsuarioSensor).filter(
        and_(
            UsuarioSensor.usuario_id == usuario_id,
            UsuarioSensor.sensor_id == sensor_id
        )
    ).first()

def get_sensores_do_usuario(db: Session, usuario_id: int):
    """Obtém todos os sensores atribuídos a um usuário."""
    return db.query(UsuarioSensor).filter(UsuarioSensor.usuario_id == usuario_id).all()

def get_usuarios_do_sensor(db: Session, sensor_id: int):
    """Obtém todos os usuários que têm acesso a um sensor."""
    return db.query(UsuarioSensor).filter(UsuarioSensor.sensor_id == sensor_id).all()

def create_usuario_sensor(db: Session, usuario_sensor: UsuarioSensorCreate) -> UsuarioSensor:
    """Cria um novo relacionamento entre usuário e sensor."""
    db_usuario_sensor = UsuarioSensor(
        usuario_id=usuario_sensor.usuario_id,
        sensor_id=usuario_sensor.sensor_id
    )
    db.add(db_usuario_sensor)
    db.commit()
    db.refresh(db_usuario_sensor)
    return db_usuario_sensor

def delete_usuario_sensor(db: Session, usuario_id: int, sensor_id: int) -> bool:
    """Remove um relacionamento entre usuário e sensor."""
    db_usuario_sensor = get_usuario_sensor(db, usuario_id, sensor_id)
    if db_usuario_sensor:
        db.delete(db_usuario_sensor)
        db.commit()
        return True
    return False

def delete_all_sensores_do_usuario(db: Session, usuario_id: int) -> int:
    """Remove todos os sensores atribuídos a um usuário."""
    sensores = get_sensores_do_usuario(db, usuario_id)
    count = len(sensores)
    for sensor in sensores:
        db.delete(sensor)
    db.commit()
    return count