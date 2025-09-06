import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from backend.app.db.session import SessionLocal
from backend.app.models.local import Local

def populate_sensors(db: Session):
    sensors = [
        Local(nome="Cisterna Principal", tipo="CISTERNA", descricao="Cisterna de 10000L"),
        Local(nome="Aquário Sala", tipo="AQUARIO", descricao="Aquário de 200L"),
        Local(nome="Caixa d'água", tipo="CASA", descricao="Caixa d'água de 1000L"),
    ]
    for sensor in sensors:
        db.add(sensor)
    db.commit()
    print("Sensores adicionados com sucesso!")

if __name__ == "__main__":
    db = SessionLocal()
    populate_sensors(db)
