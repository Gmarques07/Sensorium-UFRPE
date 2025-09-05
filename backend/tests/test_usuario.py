import pytest
from sqlalchemy.orm import Session
from app.models.usuario import Usuario


def test_criar_usuario(db: Session):
    usuario = Usuario(
        nome="Test User",
        email="test@example.com",
        endereco="Test Address"
    )
    usuario.set_senha("testpass123")

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    assert usuario.id is not None
    assert usuario.nome == "Test User"
    assert usuario.email == "test@example.com"
    assert usuario.verificar_senha("testpass123")
    assert not usuario.verificar_senha("senhaerrada")


def test_criar_usuario_senha_vazia(db: Session):
    usuario = Usuario(
        nome="Test User 2",
        email="test2@example.com",
        endereco="Test Address 2"
    )
    usuario.set_senha("")  # Define uma senha vazia

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    assert usuario.id is not None
    assert usuario.email == "test2@example.com"
    assert not usuario.verificar_senha("qualquer_senha")


def test_usuario_to_dict(db: Session):
    usuario = Usuario(
        nome="Test User 3",
        email="test3@example.com",
        endereco="Test Address 3"
    )
    usuario.set_senha("senha_teste")

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    usuario_dict = usuario.to_dict()
    assert usuario_dict["nome"] == "Test User 3"
    assert usuario_dict["email"] == "test3@example.com"
    assert "senha_hash" not in usuario_dict  # Não deve expor o hash da senha
