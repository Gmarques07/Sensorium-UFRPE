import pytest
from fastapi.testclient import TestClient
from typing import Dict
from backend.app.models.usuario import Usuario
from backend.app.models.admin import Admin
from backend.app.core.security import create_access_token

@pytest.fixture(scope="function")
def test_admin(db) -> Admin:
    admin = Admin(
        nome="Admin Teste",
        cpf="12345678901",
        email="admin@teste.com"
    )
    admin.set_senha("admin123")
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

@pytest.fixture(scope="function")
def admin_auth_headers(test_admin) -> Dict[str, str]:
    # Gerar token manualmente para evitar chamada de API de login
    token = create_access_token(data={"sub": test_admin.email, "type": "admin"})
    return {"Authorization": f"Bearer {token}"}

def test_admin_delete_user_endpoint(client: TestClient, admin_auth_headers: Dict[str, str], db):
    """
    Testa o endpoint de exclusão de usuário pelo admin com autenticação.
    Espera-se uma resposta 204 e que o usuário não exista mais (ou esteja inativo).
    """
    # 1. Criar um usuário para ser deletado
    usuario_para_deletar = Usuario(
        nome="Usuario Delete Teste",
        email="delete@teste.com",
        endereco="Rua Delete",
        ativo=True
    )
    usuario_para_deletar.set_senha("senha123")
    db.add(usuario_para_deletar)
    db.commit()
    db.refresh(usuario_para_deletar)
    
    user_id = usuario_para_deletar.id
    
    # 2. Tentar deletar o usuário via API
    r = client.delete(f"/api/v1/admin/usuarios/{user_id}", headers=admin_auth_headers)
    
    # 3. Verificar se a resposta é 204 No Content
    assert r.status_code == 204
    
    # 4. Verificar no banco se o usuário foi deletado ou desativado
    db.expire_all()
    usuario_apos_delete = db.query(Usuario).filter(Usuario.id == user_id).first()
    
    assert usuario_apos_delete is not None
    assert usuario_apos_delete.ativo is False

def test_admin_delete_nonexistent_user(client: TestClient, admin_auth_headers: Dict[str, str]):
    """
    Testa a exclusão de um usuário que não existe.
    Espera-se 404.
    """
    r = client.delete("/api/v1/admin/usuarios/999999", headers=admin_auth_headers)
    assert r.status_code == 404