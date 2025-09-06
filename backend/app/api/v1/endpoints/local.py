from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.crud import local as crud_local
from backend.app.schemas import local as schemas
from backend.app.api.deps import get_db, get_current_user
from backend.app.models.usuario import Usuario
from backend.app.models.local import Local

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
    response_model=schemas.DadosCisternaResponse,
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
        DadosCisternaResponse: Objeto contendo as últimas leituras
            - ph_atual: Nível atual do pH (0-14)
            - nivel_atual: Nível atual da água (0-100%)
            - historico_ph: Histórico de leituras de pH
            - historico_nivel: Histórico de leituras de nível
            
    Raises:
        HTTPException:
            - 401: Usuário não autenticado
            - 404: Dados não encontrados
            
    Examples:
        >>> # Python
        >>> import requests
        >>> headers = {"Authorization": f"Bearer {token}"}
        >>> response = requests.get(
        ...     "http://localhost:8000/api/v1/locais/1/dados-atuais",
        ...     headers=headers
        ... )
        >>> dados = response.json()
    """
    # TODO: Verificar se o usuário tem acesso ao local
    ph_atual, historico_ph, nivel_atual, historico_nivel = crud_local.obter_dados_cisterna(db)
    return schemas.DadosCisternaResponse(
        ph_atual=ph_atual,
        nivel_atual=nivel_atual,
        historico_ph=historico_ph,
        historico_nivel=historico_nivel
    )

@router.get(
    "/dados-atuais",
    response_model=schemas.DadosCisternaResponse,
    status_code=status.HTTP_200_OK,
    summary="Dados Atuais (Compatibilidade)",
    response_description="Últimas leituras dos sensores (endpoint de compatibilidade)",
    tags=["locais"]
)
async def obter_dados_atuais_compatibilidade(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    """
    Endpoint de compatibilidade para obter dados atuais.
    Retorna os dados do primeiro local disponível.
    """
    ph_atual, historico_ph, nivel_atual, historico_nivel = crud_local.obter_dados_cisterna(db)
    return schemas.DadosCisternaResponse(
        ph_atual=ph_atual,
        nivel_atual=nivel_atual,
        historico_ph=historico_ph,
        historico_nivel=historico_nivel
    )

@router.get(
    "/{local_id}/historico-ph",
    response_model=List[schemas.PhNivel],
    status_code=status.HTTP_200_OK,
    summary="Histórico de Leituras de pH",
    response_description="Lista de leituras de pH do local",
    tags=["locais"]
)
async def obter_historico_ph(
    local_id: int,
    limite: int = 10,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    """
    Retorna o histórico de leituras de pH do local.
    
    Args:
        local_id: ID do local
        limite: Número de registros para retornar (padrão: 10)
        
    Returns:
        List[PhNivel]: Lista de leituras de pH
        
    Raises:
        HTTPException:
            - 401: Usuário não autenticado
            - 404: Dados não encontrados
    """
    # TODO: Verificar se o usuário tem acesso ao local
    return crud_local.obter_historico_ph(db, limite)

@router.get(
    "/{local_id}/historico-nivel",
    response_model=List[schemas.NivelAgua],
    status_code=status.HTTP_200_OK,
    summary="Histórico de Leituras de Nível",
    response_description="Lista de leituras de nível do local",
    tags=["locais"]
)
async def obter_historico_nivel(
    local_id: int,
    limite: int = 10,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    """
    Retorna o histórico de leituras de nível do local.
    
    Args:
        local_id: ID do local
        limite: Número de registros para retornar (padrão: 10)
        
    Returns:
        List[NivelAgua]: Lista de leituras de nível
        
    Raises:
        HTTPException:
            - 401: Usuário não autenticado
            - 404: Dados não encontrados
    """
    # TODO: Verificar se o usuário tem acesso ao local
    return crud_local.obter_historico_nivel(db, limite)

@router.post(
    "/{local_id}/registrar-ph",
    response_model=schemas.PhNivel,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar Nova Leitura de pH",
    response_description="Leitura de pH registrada com sucesso",
    tags=["locais"]
)
async def registrar_leitura_ph(
    local_id: int,
    leitura: schemas.PhNivelCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    """
    Registra uma nova leitura de pH do local.
    
    Args:
        local_id: ID do local
        leitura: Dados da nova leitura de pH
            - ph: Nível do pH (0-14)
            
    Returns:
        PhNivel: Objeto com a leitura registrada
        
    Raises:
        HTTPException:
            - 401: Usuário não autenticado
            - 400: Dados inválidos
    """
    # TODO: Verificar se o usuário tem acesso ao local
    # TODO: Verificar se o usuário tem permissão para registrar leituras
    return crud_local.criar_ph_nivel(db, leitura, local_id=local_id)

@router.post(
    "/{local_id}/registrar-nivel",
    response_model=schemas.NivelAgua,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar Nova Leitura de Nível",
    response_description="Leitura de nível registrada com sucesso",
    tags=["locais"]
)
async def registrar_leitura_nivel(
    local_id: int,
    leitura: schemas.NivelAguaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    """
    Registra uma nova leitura de nível do local.
    
    Args:
        local_id: ID do local
        leitura: Dados da nova leitura de nível
            - boia: Nível da boia (0-100%)
            - status: Status do nível (NORMAL, BAIXO, CRITICO)
            
    Returns:
        NivelAgua: Objeto com a leitura registrada
        
    Raises:
        HTTPException:
            - 401: Usuário não autenticado
            - 400: Dados inválidos
    """
    # TODO: Verificar se o usuário tem acesso ao local
    # TODO: Verificar se o usuário tem permissão para registrar leituras
    return crud_local.criar_nivel_agua(db, leitura, local_id=local_id)