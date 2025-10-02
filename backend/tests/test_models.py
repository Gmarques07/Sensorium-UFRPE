import pytest
from sqlalchemy.orm import Session

from backend.app.schemas.leitura import PhNivelCreate, BoiaNivelCreate
from backend.app.crud import local as crud_local
from backend.app.models import Local, BoiaNivel

def test_ph_nivel(db: Session):
    local = Local(nome="Local Teste", tipo="CISTERNA", descricao="Teste")
    db.add(local)
    db.commit()
    db.refresh(local)

    ph_in = PhNivelCreate(ph=7.5)
    ph = crud_local.criar_ph_nivel(db, ph_in, local_id=local.id)
    assert ph.ph == 7.5

    # Teste de validação de pH
    with pytest.raises(ValueError):
        PhNivelCreate(ph=15.0)  # pH deve estar entre 0 e 14

def test_boia_nivel(db: Session):
    local = Local(nome="Local Teste", tipo="CISTERNA", descricao="Teste")
    db.add(local)
    db.commit()
    db.refresh(local)

    nivel_in = BoiaNivelCreate(valor=90, status="ALTO")
    nivel = crud_local.criar_boia_nivel(db, nivel_in, local_id=local.id)
    assert nivel.valor == 90
    assert nivel.status == "ALTO"

    # Teste de validação do nível
    with pytest.raises(ValueError):
        BoiaNivelCreate(valor=101, status="NORMAL")  # valor deve estar entre 0 e 100
