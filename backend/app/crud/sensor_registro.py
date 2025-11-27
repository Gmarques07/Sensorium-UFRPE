from sqlalchemy.orm import Session
from sqlalchemy import and_
from backend.app.models.usuario_sensor import UsuarioSensor
from backend.app.models.local import Local
from backend.app.schemas.usuario_sensor import UsuarioSensorCreate
from backend.app.schemas.local import LocalCreate
from backend.app.schemas.sensor_registro import SensorRegistroResponse
from backend.app.crud.local import criar_local_com_chave


def criar_sensor_para_usuario(
    db: Session,
    local_create: LocalCreate,
    usuario_id: int
) -> SensorRegistroResponse:
    """
    Cria um novo sensor e o associa ao usuário.

    Args:
        db: Sessão do banco de dados
        local_create: Dados para criação do local/sensor
        usuario_id: ID do usuário que está criando o sensor

    Returns:
        SensorRegistroResponse: Informações do sensor criado com a chave de API
    """
    # Cria o local/sensor com uma chave de API
    db_local = criar_local_com_chave(db, local_create)

    # Cria a associação entre usuário e sensor
    usuario_sensor = UsuarioSensor(usuario_id=usuario_id, sensor_id=db_local.id)
    db.add(usuario_sensor)
    db.commit()

    # Retorna a resposta com a chave de API
    return SensorRegistroResponse(
        id=db_local.id,
        nome=db_local.nome,
        tipo=db_local.tipo,
        descricao=db_local.descricao,
        chave_api=db_local.chave_api,
        data_criacao=db_local.data_criacao
    )


def criar_sensor_admin(
    db: Session,
    local_create: LocalCreate
) -> SensorRegistroResponse:
    """
    Cria um novo sensor pelo admin (sem associação a usuário).

    Args:
        db: Sessão do banco de dados
        local_create: Dados para criação do local/sensor

    Returns:
        SensorRegistroResponse: Informações do sensor criado com a chave de API
    """
    # Cria o local/sensor com uma chave de API
    db_local = criar_local_com_chave(db, local_create)

    # Retorna a resposta com a chave de API (sem associação de usuário)
    return SensorRegistroResponse(
        id=db_local.id,
        nome=db_local.nome,
        tipo=db_local.tipo,
        descricao=db_local.descricao,
        chave_api=db_local.chave_api,
        data_criacao=db_local.data_criacao
    )


def get_sensores_do_usuario(db: Session, usuario_id: int) -> list[Local]:
    """
    Obtém todos os sensores associados a um usuário.
    
    Args:
        db: Sessão do banco de dados
        usuario_id: ID do usuário
    
    Returns:
        list[Local]: Lista de sensores associados ao usuário
    """
    return db.query(Local).join(UsuarioSensor).filter(
        UsuarioSensor.usuario_id == usuario_id
    ).all()


def associar_sensor_ao_usuario(db: Session, usuario_id: int, sensor_id: int) -> bool:
    """
    Associa um sensor existente a um usuário.
    
    Args:
        db: Sessão do banco de dados
        usuario_id: ID do usuário
        sensor_id: ID do sensor
    
    Returns:
        bool: True se a associação foi bem-sucedida, False caso contrário
    """
    # Verificar se a associação já existe
    assoc = db.query(UsuarioSensor).filter(
        and_(
            UsuarioSensor.usuario_id == usuario_id,
            UsuarioSensor.sensor_id == sensor_id
        )
    ).first()
    
    if assoc:
        return False  # Associação já existe
    
    # Cria a nova associação
    usuario_sensor = UsuarioSensor(usuario_id=usuario_id, sensor_id=sensor_id)
    db.add(usuario_sensor)
    db.commit()
    
    return True