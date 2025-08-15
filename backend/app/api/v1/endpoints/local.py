from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ....crud import local as crud_local
from ....schemas import local as schemas
from ....api.deps import get_db, get_current_user
from ....models.usuario import Usuario
from ....models.local import Local

router = APIRouter()

@router.post(
    "/",
    response_model=schemas.Local,
    status_code=status.HTTP_201_CREATED,
    summary="Criar Novo Local",
    response_description="Local criado com sucesso",
    tags=["locais"]
)
async def criar_local(
    local: schemas.LocalCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    """
    Cria um novo local para monitoramento.
    
    Args:
        local: Dados do local
            - nome: Nome do local
            - tipo: Tipo do local (CISTERNA, AQUARIO, CASA)
            - descricao: Descrição opcional
            
    Returns:
        Local: Local criado
    """
    return crud_local.criar_local(db, local)

@router.get(
    "/{local_id}/dados-atuais",
    response_model=schemas.Leitura,
    status_code=status.HTTP_200_OK,
    summary="Dados Atuais do Local",
    response_description="Últimas leituras dos sensores do local",
    tags=["locais"]
)
async def obter_dados_atuais(
    local_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    """
    Retorna os dados mais recentes dos sensores do local.
    
    Args:
        local_id: ID do local
        
    Returns:
        Leitura: Objeto contendo as últimas leituras
            - local: Dados do local
            - ph: Nível atual do pH (0-14)
            - boia: Nível atual da água (0-100%)
            - ultima_atualizacao: Data/hora da última leitura
            
    Raises:
        HTTPException:
            - 401: Usuário não autenticado
            - 404: Dados não encontrados
            
    Examples:
        >>> # Python
        >>> import requests
        >>> headers = {"Authorization": f"Bearer {token}"}
        >>> response = requests.get(
        ...     "http://localhost:8000/api/v1/cisterna/dados-atuais",
        ...     headers=headers
        ... )
        >>> dados = response.json()
    """
    return crud_cisterna.get_ultima_leitura(db)

@router.get(
    "/historico",
    response_model=List[schemas.CisternaLeitura],
    status_code=status.HTTP_200_OK,
    summary="Histórico de Leituras",
    response_description="Lista de leituras dos sensores da cisterna",
    tags=["cisterna"]
)
async def obter_historico(
    periodo: int = 7,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    """
    Retorna o histórico de leituras dos sensores da cisterna.
    
    Args:
        periodo: Número de dias para retornar o histórico (padrão: 7)
        
    Returns:
        List[CisternaLeitura]: Lista de leituras dos sensores
            - nivel_agua: Nível da água (%)
            - ph: Nível do pH
            - temperatura: Temperatura (°C)
            - data_hora: Data/hora da leitura
            
    Raises:
        HTTPException:
            - 401: Usuário não autenticado
            - 404: Dados não encontrados
            
    Examples:
        >>> # Python
        >>> import requests
        >>> headers = {"Authorization": f"Bearer {token}"}
        >>> params = {"periodo": 30}  # Últimos 30 dias
        >>> response = requests.get(
        ...     "http://localhost:8000/api/v1/cisterna/historico",
        ...     headers=headers,
        ...     params=params
        ... )
        >>> historico = response.json()
    """
    return crud_cisterna.get_historico(db, periodo)

@router.post(
    "/registrar-leitura",
    response_model=schemas.CisternaLeitura,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar Nova Leitura",
    response_description="Leitura registrada com sucesso",
    tags=["cisterna"]
)
async def registrar_leitura(
    leitura: schemas.CisternaLeituraCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    """
    Registra uma nova leitura dos sensores da cisterna.
    
    Args:
        leitura: Dados da nova leitura
            - nivel_agua: Nível da água (%)
            - ph: Nível do pH
            - temperatura: Temperatura (°C)
            
    Returns:
        CisternaLeitura: Objeto com a leitura registrada
        
    Raises:
        HTTPException:
            - 401: Usuário não autenticado
            - 400: Dados inválidos
            
    Examples:
        >>> # Python
        >>> import requests
        >>> headers = {"Authorization": f"Bearer {token}"}
        >>> dados = {
        ...     "nivel_agua": 85.5,
        ...     "ph": 7.2,
        ...     "temperatura": 25.3
        ... }
        >>> response = requests.post(
        ...     "http://localhost:8000/api/v1/cisterna/registrar-leitura",
        ...     headers=headers,
        ...     json=dados
        ... )
        >>> leitura = response.json()
    """
    if not current_user.tipo == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem registrar leituras"
        )
    return crud_cisterna.create_leitura(db, leitura)
