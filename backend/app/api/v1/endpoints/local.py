from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.crud import local as crud_local
from backend.app.schemas import local as schemas_local, leitura as schemas_leitura
from backend.app.api.deps import get_db, get_current_user_from_cookie
from backend.app.models.usuario import Usuario
from backend.app.models import Local as LocalModel

router = APIRouter()

@router.get(
    "/",
    response_model=List[schemas_local.Local],
    status_code=status.HTTP_200_OK,
    summary="Listar Locais do Usuário",
    response_description="Lista de locais/sensores do usuário",
    tags=["locais"]
)
async def listar_locais_do_usuario(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
) -> Any:
    # Importar localmente para evitar loops de importação
    from backend.app.models.usuario_sensor import UsuarioSensor
    from sqlalchemy import and_

    # Obter os IDs dos locais associados ao usuário
    sensor_ids = db.query(UsuarioSensor.sensor_id).filter(
        UsuarioSensor.usuario_id == current_user.id
    ).all()

    # Filtrar os locais com base nos IDs
    sensor_ids_list = [id[0] for id in sensor_ids]  # Extrai os IDs da tupla
    if not sensor_ids_list:
        return []

    locais = db.query(LocalModel).filter(LocalModel.id.in_(sensor_ids_list)).all()
    return locais

@router.post(
    "/",
    response_model=schemas_local.LocalWithKey,
    status_code=status.HTTP_201_CREATED,
    summary="Criar Novo Local",
    response_description="Local criado com sucesso",
    tags=["locais"]
)
async def criar_local(
    local: schemas_local.LocalCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
) -> Any:
    return crud_local.criar_local(db, local)

@router.get(
    "/{local_id}/dados-atuais",
    response_model=schemas_leitura.DadosCisternaResponse,
    status_code=status.HTTP_200_OK,
    summary="Dados Atuais do Local",
    response_description="Últimas leituras dos sensores do local",
    tags=["locais"]
)
async def obter_dados_atuais(
    local_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
) -> Any:
    ph_atual, historico_ph, nivel_atual, historico_nivel, umidade_atual, historico_umidade = crud_local.obter_dados_cisterna(db, local_id)
    return schemas_leitura.DadosCisternaResponse(
        ph_atual=ph_atual,
        nivel_atual=nivel_atual,
        umidade_atual=umidade_atual,
        historico_ph=historico_ph,
        historico_nivel=historico_nivel,
        historico_umidade=historico_umidade
    )

@router.get(
    "/dados-atuais",
    response_model=schemas_leitura.DadosCisternaResponse,
    status_code=status.HTTP_200_OK,
    summary="Dados Atuais (Compatibilidade)",
    response_description="Últimas leituras dos sensores (endpoint de compatibilidade)",
    tags=["locais"]
)
async def obter_dados_atuais_compatibilidade(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
) -> Any:
    # Assuming the first local is the target for compatibility
    local = db.query(LocalModel).first()
    if not local:
        raise HTTPException(status_code=404, detail="Nenhum local encontrado")
    ph_atual, historico_ph, nivel_atual, historico_nivel, umidade_atual, historico_umidade = crud_local.obter_dados_cisterna(db, local.id)
    return schemas_leitura.DadosCisternaResponse(
        ph_atual=ph_atual,
        nivel_atual=nivel_atual,
        umidade_atual=umidade_atual,
        historico_ph=historico_ph,
        historico_nivel=historico_nivel,
        historico_umidade=historico_umidade
    )

@router.get(
    "/{local_id}/historico-ph",
    response_model=List[schemas_leitura.PhNivel],
    status_code=status.HTTP_200_OK,
    summary="Histórico de Leituras de pH",
    response_description="Lista de leituras de pH do local",
    tags=["locais"]
)
async def obter_historico_ph(
    local_id: int,
    limite: int = 10,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
) -> Any:
    return crud_local.obter_historico_ph(db, local_id, limite)

@router.get(
    "/{local_id}/historico-nivel-boia",
    response_model=List[schemas_leitura.BoiaNivel],
    status_code=status.HTTP_200_OK,
    summary="Histórico de Leituras de Nível da Bóia",
    response_description="Lista de leituras de nível da bóia do local",
    tags=["locais"]
)
async def obter_historico_nivel_boia(
    local_id: int,
    limite: int = 10,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
) -> Any:
    return crud_local.obter_historico_nivel_boia(db, local_id, limite)

@router.post(
    "/{local_id}/registrar-ph",
    response_model=schemas_leitura.PhNivel,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar Nova Leitura de pH",
    response_description="Leitura de pH registrada com sucesso",
    tags=["locais"]
)
async def registrar_leitura_ph(
    local_id: int,
    leitura: schemas_leitura.PhNivelCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
) -> Any:
    return crud_local.criar_ph_nivel(db, leitura, local_id=local_id)

@router.post(
    "/{local_id}/registrar-nivel-boia",
    response_model=schemas_leitura.BoiaNivel,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar Nova Leitura de Nível da Bóia",
    response_description="Leitura de nível da bóia registrada com sucesso",
    tags=["locais"]
)
async def registrar_leitura_boia(
    local_id: int,
    leitura: schemas_leitura.BoiaNivelCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
) -> Any:
    return crud_local.criar_boia_nivel(db, leitura, local_id=local_id)

@router.delete(
    "/{local_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir Local",
    response_description="Local excluído com sucesso",
    tags=["locais"]
)
async def excluir_local(
    local_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
) -> None:
    # Verificar se o local está associado ao usuário atual
    from backend.app.models.usuario_sensor import UsuarioSensor
    from sqlalchemy import and_

    assoc = db.query(UsuarioSensor).filter(
        and_(
            UsuarioSensor.usuario_id == current_user.id,
            UsuarioSensor.sensor_id == local_id
        )
    ).first()

    if not assoc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Local não encontrado ou você não tem permissão para excluí-lo"
        )

    # Remover a associação na tabela intermediária primeiro
    from backend.app.crud import usuario_sensor as crud_usuario_sensor
    crud_usuario_sensor.delete_usuario_sensor(db, current_user.id, local_id)

    # Em seguida, excluir o local (e suas leituras associadas)
    success = crud_local.deletar_local(db, local_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Local não encontrado"
        )

