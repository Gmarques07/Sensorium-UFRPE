import pytest
from sqlalchemy.orm import Session

from app.schemas.usuario import UsuarioCreate
from app.schemas.local import PhNivelCreate, NivelAguaCreate
from app.crud import usuario as crud_usuario
from app.crud import local as crud_cisterna
from app.models.local import NivelAgua, Local


def test_dummy():
    assert True


def test_criar_usuario(db: Session):
    usuario_in = UsuarioCreate(
        nome="Test User",
        email="test@example.com",
        endereco="Test Address",
        senha="testpass123"
    )
    usuario = crud_usuario.create_usuario(db, usuario_in)
    assert usuario.nome == usuario_in.nome
    assert usuario.email == usuario_in.email
    assert usuario.verificar_senha("testpass123")


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

    nivel_in = NivelAguaCreate(boia=75, status="NORMAL")
    nivel = crud_cisterna.criar_nivel_agua(db, nivel_in, local_id=local.id)
    assert nivel.boia == 75
    assert nivel.status == "NORMAL"

    # Teste do cálculo de status
    assert NivelAgua.calcular_status(80) == "NORMAL"
    assert NivelAgua.calcular_status(30) == "BAIXO"
    assert NivelAgua.calcular_status(20) == "CRITICO"

    # Teste de validação do nível
    with pytest.raises(ValueError):
        NivelAguaCreate(boia=101, status="NORMAL")  # boia deve estar entre 0 e 100
