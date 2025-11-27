import pytest
from fastapi.testclient import TestClient
from typing import Dict
from backend.app.models.usuario import Usuario
from backend.app.models.admin import Admin
from backend.app.core.security import create_access_token

@pytest.fixture(scope="function")
def test_admin_cookie(db) -> Admin:
    admin = Admin(
        nome="Admin Cookie Teste",
        cpf="98765432101",
        email="admin_cookie@teste.com"
    )
    admin.set_senha("admin123")
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

def test_admin_delete_user_with_cookie(client: TestClient, test_admin_cookie: Admin, db):
    """
    Testa o endpoint de exclusão de usuário pelo admin usando COOKIE em vez de Header.
    """
    # 1. Gerar token
    token = create_access_token(data={"sub": test_admin_cookie.email, "type": "admin"})
    
    # 2. Criar um usuário para ser deletado
    usuario_para_deletar = Usuario(
        nome="Usuario Delete Cookie",
        email="delete_cookie@teste.com",
        endereco="Rua Cookie",
        ativo=True
    )
    usuario_para_deletar.set_senha("senha123")
    db.add(usuario_para_deletar)
    db.commit()
    db.refresh(usuario_para_deletar)
    
    user_id = usuario_para_deletar.id
    
    # 3. Tentar deletar o usuário via API SEM header, mas COM cookie
    r = client.delete(
        f"/api/v1/admin/usuarios/{user_id}", 
        cookies={"admin_access_token": f"Bearer {token}"}
    )
    
    # 4. Verificar se a resposta é 204 No Content
    assert r.status_code == 204
    
    # 5. Verificar no banco se o usuário foi deletado ou desativado
    db.expire_all()
    usuario_apos_delete = db.query(Usuario).filter(Usuario.id == user_id).first()
    
    assert usuario_apos_delete is not None
    assert usuario_apos_delete.ativo is False

    # 6. Verificar se o usuário NÃO aparece mais na lista de usuários
    r_list = client.get("/api/v1/admin/usuarios", cookies={"admin_access_token": f"Bearer {token}"})
    assert r_list.status_code == 200
    users = r_list.json()
    user_ids = [u["id"] for u in users]
    assert user_id not in user_ids
