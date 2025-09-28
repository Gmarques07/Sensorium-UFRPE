import pytest
from sqlalchemy.orm import Session

from backend.app.schemas.local import PhNivelCreate, NivelAguaCreate
from backend.app.crud import local as crud_cisterna
from backend.app.models.local import NivelAgua, Local


def test_ph_nivel(db: Session):
    local = Local(nome="Local Teste", tipo="CISTERNA", descricao="Teste")
    db.add(local)
    db.commit()
    db.refresh(local)

    ph_in = PhNivelCreate(ph=7.5)
    ph = crud_cisterna.criar_ph_nivel(db, ph_in, local_id=local.id)
    assert ph.ph == 7.5

    # Teste de validação de pH
    with pytest.raises(ValueError):
        PhNivelCreate(ph=15.0)  # pH deve estar entre 0 e 14


def test_nivel_agua(db: Session):
    local = Local(nome="Local Teste", tipo="CISTERNA", descricao="Teste")
    db.add(local)
    db.commit()
    db.refresh(local)

    nivel_in = NivelAguaCreate(boia=90, status="ALTO")
    nivel = crud_cisterna.criar_nivel_agua(db, nivel_in, local_id=local.id)
    assert nivel.boia == 90
    assert nivel.status == "ALTO"

    # Teste do cálculo de status
    assert NivelAgua.calcular_status(90) == "ALTO"
    assert NivelAgua.calcular_status(60) == "NORMAL"
    assert NivelAgua.calcular_status(40) == "BAIXO"
    assert NivelAgua.calcular_status(10) == "CRITICO"

    # Teste de validação do nível
    with pytest.raises(ValueError):
        NivelAguaCreate(boia=101, status="NORMAL")  # boia deve estar entre 0 e 100