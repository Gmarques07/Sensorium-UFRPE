from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.app.models.leitura import Leitura, PhNivel, BoiaNivel
from backend.app.models.local import Local
from backend.app.schemas.leitura import LeituraPayload

def create_leitura_from_payload(db: Session, *, payload: LeituraPayload) -> None:
    """
    Creates Leitura, PhNivel, and BoiaNivel records from a payload.
    """
    local = db.query(Local).filter(Local.id == payload.dispositivo_id).first()
    if not local:
        local = db.query(Local).filter(Local.id == 1).first()
        if not local:
            raise HTTPException(status_code=404, detail=f"Local with id {payload.dispositivo_id} not found and default local with id 1 also not found.")

    # Create Leitura for pH
    leitura_ph = Leitura(
        local_id=local.id,
        sensor_tipo='PH'
    )
    db.add(leitura_ph)
    db.flush()  # Flush to get the ID for leitura_ph

    ph_nivel = PhNivel(
        leitura_id=leitura_ph.id,
        ph=payload.ph
    )
    db.add(ph_nivel)

    # Create Leitura for Boia
    leitura_boia = Leitura(
        local_id=local.id,
        sensor_tipo='BOIA'
    )
    db.add(leitura_boia)
    db.flush()  # Flush to get the ID for leitura_boia

    boia_nivel = BoiaNivel(
        leitura_id=leitura_boia.id,
        valor=payload.boia,
        status=payload.status_boia.upper()
    )
    db.add(boia_nivel)
    
    db.commit()
