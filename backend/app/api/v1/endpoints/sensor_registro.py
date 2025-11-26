from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.crud import sensor_registro as crud_sensor_registro
from backend.app.schemas import sensor_registro as schemas_sensor_registro
from backend.app.api.deps import get_db, get_current_user
from backend.app.models.usuario import Usuario

router = APIRouter()

@router.post(
    "/registrar-sensor",
    response_model=schemas_sensor_registro.SensorRegistroResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar Novo Sensor pelo Usuário",
    response_description="Sensor criado e associado ao usuário",
    tags=["sensores"]
)
async def registrar_sensor(
    sensor_registro: schemas_sensor_registro.SensorRegistroCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    """
    Permite que um usuário registre um novo sensor (local).
    O sensor é automaticamente associado à conta do usuário.
    """
    try:
        return crud_sensor_registro.criar_sensor_para_usuario(
            db,
            sensor_registro,
            current_user.id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao registrar sensor: {str(e)}"
        )