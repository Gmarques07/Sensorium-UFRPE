from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.app.models.notificacao import Notificacao
from backend.app.models import Local

# Este teste agora é um teste de integração que usa o TestClient e o banco de dados em memória
# Isso permite um controle mais refinado sobre o estado do banco de dados para testar o fluxo de notificações

def test_notificacoes_fluxo_completo(client: TestClient, db: Session):
    # 1. Criar um usuário de teste
    user_email = "notif_user@example.com"
    user_password = "a_secure_password"
    response = client.post(
        "/api/v1/auth/registro",
        json={
            "nome": "Notif User",
            "email": user_email,
            "endereco": "Rua Teste, 123",
            "senha": user_password,
        },
    )
    assert response.status_code == 200

    # 2. Fazer login para obter o token
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": user_email, "senha": user_password},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Verificar se não há notificações inicialmente
    response = client.get("/api/v1/notificacoes/", headers=headers)
    assert response.status_code == 200
    assert response.json() == []

    # 4. Criar um local primeiro
    local = Local(nome="Cisterna Teste", tipo="CISTERNA", descricao="Local para teste de notificações")
    db.add(local)
    db.flush()  # Flush para obter o ID sem commit
    
    # 5. Inserir manualmente uma notificação no banco de dados para este usuário
    nova_notificacao = Notificacao(
        mensagem="Alerta de teste: O pH da sua cisterna está muito baixo!",
        email_usuario=user_email,
        tipo="PH_ALTERADO",
        local_id=local.id
    )
    db.add(nova_notificacao)
    db.commit()
    db.refresh(nova_notificacao)
    notificacao_id = nova_notificacao.id

    # 6. Listar notificações e verificar se a nova notificação está lá
    response = client.get("/api/v1/notificacoes/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == notificacao_id
    assert data[0]["mensagem"] == "Alerta de teste: O pH da sua cisterna está muito baixo!"
    assert not data[0]["lida"]

    # 7. Verificar se a notificação aparece como não lida
    response = client.get("/api/v1/notificacoes/nao-lidas", headers=headers)
    assert response.status_code == 200
    data_nao_lida = response.json()
    assert len(data_nao_lida) == 1
    assert data_nao_lida[0]["id"] == notificacao_id

    # 8. Marcar a notificação como lida
    response = client.post(f"/api/v1/notificacoes/{notificacao_id}/marcar-como-lida", headers=headers)
    assert response.status_code == 200
    assert response.json()["lida"]

    # 9. Verificar se a notificação não está mais na lista de não lidas
    response = client.get("/api/v1/notificacoes/nao-lidas", headers=headers)
    assert response.status_code == 200
    assert response.json() == []

