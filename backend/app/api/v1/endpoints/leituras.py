print("leituras.py loaded")
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.api import deps
from backend.app.schemas.leitura import LeituraPayload
from backend.app.crud.leitura import create_leitura_from_payload

router = APIRouter()

@router.post("/", status_code=201)
def create_leitura(
    *,
    db: Session = Depends(deps.get_db),
    payload: LeituraPayload
):
    """
    Create new leitura.
    """
    create_leitura_from_payload(db=db, payload=payload)
    return {"msg": "Leitura created successfully"}
