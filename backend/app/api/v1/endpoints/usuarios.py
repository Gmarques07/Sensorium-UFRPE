from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from ....crud import usuario as crud_usuario
from ....schemas import usuario as schemas
from ....api.deps import get_db, get_current_user
from ....core.security import get_password_hash, verify_password
from ....models.usuario import Usuario
from ....core.limiter import rate_limit
from zoneinfo import ZoneInfo

router = APIRouter()

@router.get("/perfil", 
              response_model=schemas.Usuario,
              status_code=status.HTTP_200_OK,
              summary="Obter Perfil do Usuário",
              response_description="Dados do perfil do usuário",
              tags=["usuários"])
def obter_perfil(
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    """
    Retorna o perfil completo do usuário autenticado.

    Returns:
        Usuario: Objeto contendo todos os dados do usuário
            - id: ID único do usuário
            - nome: Nome completo
            - email: Email do usuário
            - cpf: CPF do usuário
            - tipo: Tipo de usuário (comum/admin)
            - ativo: Status da conta
            
    Raises:
        HTTPException:
            - 401: Usuário não autenticado
            - 404: Usuário não encontrado
            
    Examples:
        >>> # Python
        >>> import requests
        >>> headers = {"Authorization": f"Bearer {token}"}
        >>> response = requests.get("http://localhost:8000/api/v1/usuarios/perfil", headers=headers)
        >>> perfil = response.json()
    """
    return current_user

@router.put("/editar-perfil", 
         response_model=schemas.Usuario,
         status_code=status.HTTP_200_OK,
         summary="Atualizar Perfil do Usuário",
         response_description="Perfil atualizado do usuário",
         tags=["usuários"])
def editar_perfil(
    dados_atualizacao: schemas.UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    """
    Atualiza os dados do perfil do usuário autenticado.
    
    Args:
        dados_atualizacao: Dados a serem atualizados
            - nome: Novo nome (opcional)
            - email: Novo email (opcional)
            - endereco: Novo endereço (opcional)
        current_user: Usuário atual (injetado via token)
        
    Returns:
        Usuario: Objeto com os dados atualizados do usuário
        
    Raises:
        HTTPException:
            - 401: Usuário não autenticado
            - 400: Dados inválidos
            - 409: Email já existe
            
    Examples:
        >>> # Python
        >>> import requests
        >>> headers = {"Authorization": f"Bearer {token}"}
        >>> dados = {
        ...     "nome": "Novo Nome",
        ...     "email": "novo@email.com",
        ...     "endereco": "Nova Rua, 123"
        ... }
        >>> response = requests.put(
        ...     "http://localhost:8000/api/v1/usuarios/editar-perfil",
        ...     headers=headers,
        ...     json=dados
        ... )
        >>> perfil_atualizado = response.json()
    - Se uma nova senha for fornecida, ela será hasheada antes de salvar
    """
    # Se estiver atualizando o email, verifica se já existe
    if dados_atualizacao.email and dados_atualizacao.email != current_user.email:
        usuario_existente = crud_usuario.get_usuario_by_email(db, email=dados_atualizacao.email)
        if usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este email já está em uso"
            )
    
    # Se uma nova senha foi fornecida, faz o hash
    if dados_atualizacao.senha:
        dados_atualizacao.senha = get_password_hash(dados_atualizacao.senha)
    
    usuario = crud_usuario.update_usuario(
        db, 
        usuario=current_user,
        usuario_in=dados_atualizacao
    )
    return usuario

@router.post("/validar-senha")
def validar_senha(
    senha: str,
    current_user: Usuario = Depends(get_current_user),
    __rl: None = Depends(rate_limit(5, 60, "validar-senha"))
) -> Any:
    """
    Valida a senha atual do usuário.
    Útil antes de realizar operações sensíveis.
    """
    # current_user tem o atributo senha_hash ou método verificar_senha
    if hasattr(current_user, "senha_hash"):
        ok = verify_password(senha, current_user.senha_hash)
    else:
        ok = current_user.verificar_senha(senha)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha incorreta"
        )
    return {"valid": True}

@router.delete("/excluir-conta", status_code=status.HTTP_204_NO_CONTENT)
def excluir_conta(
    senha: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Desativa a conta do usuário atual (soft delete).
    Requer a senha atual para confirmar a operação.
    """
    # Valida a senha antes de desativar
    # Verifica a senha antes de desativar
    if hasattr(current_user, "senha_hash"):
        ok = verify_password(senha, current_user.senha_hash)
    else:
        ok = current_user.verificar_senha(senha)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha incorreta"
        )
    
    # Desativa o usuário
    crud_usuario.deactivate_usuario(db, usuario=current_user)
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/dashboard-dados", 
              response_model=dict,
              status_code=status.HTTP_200_OK,
              summary="Obter Dados do Dashboard",
              response_description="Dados dos sensores para o dashboard do usuário",
              tags=["usuários"])
def obter_dados_dashboard(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    """
    Retorna os dados dos sensores para o dashboard do usuário.
    Inclui dados de pH e nível de água dos locais atribuídos ao usuário.

    Returns:
        dict: Dados dos sensores organizados por dispositivo
            - dispositivos: Lista de dispositivos/locais atribuídos ao usuário
            - ph_por_dispositivo: Dados de pH por dispositivo
            - nivel_por_dispositivo: Dados de nível por dispositivo
            
    Raises:
        HTTPException:
            - 401: Usuário não autenticado
    """
    from ....crud import local as crud_local
    from ....models.local import Local
    from ....models.usuario_sensor import UsuarioSensor
    
    # Buscar apenas os IDs dos locais atribuídos ao usuário primeiro
    local_ids = db.query(UsuarioSensor.sensor_id).filter(
        UsuarioSensor.usuario_id == current_user.id
    ).all()
    
    # Depois, buscar os detalhes completos desses locais individualmente
    dispositivos = []
    ph_por_dispositivo = {}
    nivel_por_dispositivo = {}
    
    for local_id_tuple in local_ids:
        local_id = local_id_tuple[0]
        local = db.query(Local).filter(Local.id == local_id).first()
        if local:  # Verificar se o local existe
            dispositivos.append({
                "nome": local.nome,
                "id": local.id,
                "tipo": local.tipo
            })
            
            # Carregar dados de pH e nível para este local específico
            ph_atual, historico_ph, nivel_atual, historico_nivel = crud_local.obter_dados_cisterna(db, local_id=local.id)
            
            ph_por_dispositivo[local.nome if local.nome else f"Local {local.id}"] = {
                "atual": {
                    "ph": ph_atual.ph if ph_atual and hasattr(ph_atual, 'ph') else 7.0,
                    "data": ph_atual.leitura.data.astimezone(ZoneInfo("America/Sao_Paulo")).strftime("%Y-%m-%d %H:%M:%S") if ph_atual and hasattr(ph_atual, 'leitura') and ph_atual.leitura and hasattr(ph_atual.leitura, 'data') else "N/A"
                } if ph_atual else None,
                "historico": [
                    {
                        "ph": item.ph,
                        "data": item.leitura.data.astimezone(ZoneInfo("America/Sao_Paulo")).strftime("%Y-%m-%d %H:%M:%S")
                    } for item in historico_ph
                ]
            }
            
            nivel_por_dispositivo[local.nome if local.nome else f"Local {local.id}"] = {
                "atual": {
                    "status": nivel_atual.status if nivel_atual and hasattr(nivel_atual, 'status') else "NORMAL",
                    "valor": nivel_atual.valor if nivel_atual and hasattr(nivel_atual, 'valor') else 0,
                    "data": nivel_atual.leitura.data.astimezone(ZoneInfo("America/Sao_Paulo")).strftime("%Y-%m-%d %H:%M:%S") if nivel_atual and hasattr(nivel_atual, 'leitura') and nivel_atual.leitura and hasattr(nivel_atual.leitura, 'data') else "N/A"
                } if nivel_atual else None,
                "historico": [
                    {
                        "status": item.status,
                        "data": item.leitura.data.astimezone(ZoneInfo("America/Sao_Paulo")).strftime("%Y-%m-%d %H:%M:%S")
                    } for item in historico_nivel
                ]
            }

    # Se não há locais atribuídos, retornar dados vazios
    if not dispositivos:
        return {
            "dispositivos": [],
            "ph_por_dispositivo": {},
            "nivel_por_dispositivo": {}
        }
    
    return {
        "dispositivos": dispositivos,
        "ph_por_dispositivo": ph_por_dispositivo,
        "nivel_por_dispositivo": nivel_por_dispositivo
    }