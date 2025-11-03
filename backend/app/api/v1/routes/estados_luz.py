from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.api.deps import get_db

router = APIRouter()

# Modelo do JSON que a ESP vai enviar
class EstadoLuzRequest(BaseModel):
    estado: str

@router.post("/estados-luz")
def receber_estado_luz(data: EstadoLuzRequest, db: Session = Depends(get_db)):
    try:
        # Validação do estado
        estado = data.estado.lower().strip()
        if estado not in ["ligado", "desligado"]:
            raise HTTPException(status_code=400, detail="Estado deve ser 'ligado' ou 'desligado'")
        
        horario_atual = datetime.now()
        
        # Usando SQLAlchemy com text() para evitar problemas de mapeamento
        query = text("INSERT INTO estados_luz (estado, horario) VALUES (:estado, :horario)")
        db.execute(query, {"estado": estado, "horario": horario_atual})
        db.commit()
        
        return {"status": "ok", "mensagem": "Estado registrado com sucesso!"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao registrar estado: {str(e)}")

@router.get("/estados-luz")
def obter_estados_luz(db: Session = Depends(get_db)):
    try:
        query = text("SELECT id, estado, horario FROM estados_luz ORDER BY horario DESC LIMIT 50")
        result = db.execute(query)
        estados = []
        for row in result:
            estados.append({
                "id": row[0],
                "estado": row[1],
                "horario": row[2].isoformat() if row[2] else None
            })
        return {"estados": estados}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar estados: {str(e)}")