print("leituras.py loaded")
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.api import deps
from backend.app.schemas.leitura import LeituraPayload
from backend.app.crud.leitura import create_leitura_from_payload
from backend.app.models.local import Local
from backend.app.models.usuario import Usuario

router = APIRouter()

@router.post("/", status_code=201)
def create_leitura(
    *,
    db: Session = Depends(deps.get_db),
    sensor: Optional[Local] = Depends(deps.get_sensor_by_api_key_strict),  # API key validation
    current_user: Optional[Usuario] = Depends(deps.get_current_user_optional),  # User token validation (optional)
    payload: LeituraPayload
):
    """
    Create new leitura using API key or user token authentication.
    Requires either a valid API key or a valid user token.
    If API key is provided and valid, it will override the dispositivo_id in the payload.
    """
    # Check if either API key or user token is valid
    if not sensor and not current_user:
        raise HTTPException(
            status_code=401,
            detail="Either API key or user token is required for authentication"
        )

    # If authenticated via API key, use the sensor ID from the API key instead of payload
    if sensor:
        payload.dispositivo_id = sensor.id
    # If authenticated via user token, use the dispositivo_id from payload
    # This maintains backward compatibility with existing systems

    # Validate that dispositivo_id is provided either from API key or payload
    if not payload.dispositivo_id:
        raise HTTPException(
            status_code=400,
            detail="Dispositivo ID is required"
        )

    create_leitura_from_payload(db=db, payload=payload)
    return {"msg": "Leitura created successfully", "sensor_id": payload.dispositivo_id}
