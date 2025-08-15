from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ....crud import notificacao as crud_notificacao
from ....schemas import notificacao as schemas
from ....api.deps import get_db, get_current_user, get_current_admin
from ....models.usuario import Usuario

router = APIRouter()

@router.get(
    "/",
    response_model=List[schemas.Notificacao],
    status_code=status.HTTP_200_OK,
    summary="Listar Notificações do Usuário",
    response_description="Lista paginada de notificações do usuário",
    tags=["notificações"]
)
def listar_notificacoes(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Retorna uma lista paginada das notificações do usuário atual.
    
    Args:
        skip: Número de registros para pular (paginação)
        limit: Número máximo de registros para retornar (padrão: 10)
        
    Returns:
        List[Notificacao]: Lista de notificações do usuário
            - id: ID da notificação
            - titulo: Título da notificação
            - mensagem: Conteúdo
            - tipo: Tipo (alerta, info, erro)
            - data_criacao: Data de criação
            - lida: Status de leitura
            
    Raises:
        HTTPException:
            - 401: Usuário não autenticado
            
    Examples:
        >>> # Python
        >>> import requests
        >>> headers = {"Authorization": f"Bearer {token}"}
        >>> params = {"skip": 0, "limit": 20}
        >>> response = requests.get(
        ...     "http://localhost:8000/api/v1/notificacoes",
        ...     headers=headers,
        ...     params=params
        ... )
        >>> notificacoes = response.json()
    """
    notificacoes = crud_notificacao.get_notificacoes_usuario(
        db, current_user.id, skip=skip, limit=limit
    )
    return notificacoes

@router.get(
    "/nao-lidas",
    response_model=List[schemas.Notificacao],
    status_code=status.HTTP_200_OK,
    summary="Listar Notificações Não Lidas",
    response_description="Lista de notificações não lidas do usuário",
    tags=["notificações"]
)
def listar_notificacoes_nao_lidas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Retorna uma lista das notificações não lidas do usuário atual.
    Limita a 10 notificações mais recentes.
    """
    notificacoes = crud_notificacao.get_notificacoes_usuario(
        db, current_user.id, limit=10
    )
    return [n for n in notificacoes if not n.lida]

@router.post("/{notificacao_id}/marcar-como-lida", response_model=schemas.Notificacao)
def marcar_como_lida(
    notificacao_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Marca uma notificação específica como lida.
    
    Parâmetros:
    - notificacao_id: ID da notificação a ser marcada como lida
    
    Retorna:
    - A notificação atualizada
    
    Erros:
    - 404: Se a notificação não for encontrada
    - 403: Se a notificação não pertencer ao usuário atual
    """
    notificacao = crud_notificacao.get_notificacao(db, notificacao_id)
    if not notificacao:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    
    # Verifica se a notificação pertence ao usuário
    if notificacao.cpf_usuario != current_user.cpf:
        raise HTTPException(status_code=403, detail="Acesso não autorizado")
    
    return crud_notificacao.update_notificacao(
        db, notificacao_id, schemas.NotificacaoUpdate(lida=True)
    )

# Endpoints para Admin

@router.get("/admin", response_model=List[schemas.NotificacaoAdmin])
def listar_notificacoes_admin(
    apenas_nao_lidas: bool = False,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin)  # Garante que apenas admin pode acessar
):
    """
    Lista todas as notificações administrativas do sistema.
    
    Parâmetros:
    - apenas_nao_lidas: Se verdadeiro, retorna apenas notificações não lidas
    - skip: Número de registros para pular (paginação)
    - limit: Número máximo de registros para retornar
    
    Requer:
    - Usuário autenticado com privilégios de administrador
    """
    notificacoes = crud_notificacao.get_notificacoes_admin(
        db, apenas_nao_lidas=apenas_nao_lidas, skip=skip, limit=limit
    )
    return notificacoes

@router.post("/admin/criar", response_model=schemas.NotificacaoAdmin)
def criar_notificacao_admin(
    notificacao: schemas.NotificacaoCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin)
):
    """
    Cria uma nova notificação administrativa no sistema.
    
    Parâmetros:
    - notificacao: Dados da notificação a ser criada
    
    Requer:
    - Usuário autenticado com privilégios de administrador
    
    Observações:
    - O título será automaticamente gerado a partir dos primeiros 200 caracteres da mensagem
    - O tipo será definido como 'geral' por padrão
    """
    return crud_notificacao.create_notificacao_admin(
        db,
        tipo="geral",
        titulo=notificacao.mensagem[:200],  # Usa os primeiros 200 caracteres como título
        mensagem=notificacao.mensagem
    )

@router.post("/admin/{notificacao_id}/marcar-como-lida", response_model=schemas.NotificacaoAdmin)
def marcar_notificacao_admin_como_lida(
    notificacao_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin)
):
    """
    Marca uma notificação administrativa específica como lida.
    
    Parâmetros:
    - notificacao_id: ID da notificação administrativa a ser marcada como lida
    
    Requer:
    - Usuário autenticado com privilégios de administrador
    
    Erros:
    - 404: Se a notificação administrativa não for encontrada
    """
    notificacao = crud_notificacao.marcar_notificacao_admin_como_lida(db, notificacao_id)
    if not notificacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação administrativa não encontrada"
        )
    return notificacao
