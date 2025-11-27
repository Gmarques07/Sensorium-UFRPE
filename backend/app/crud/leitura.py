from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.app.models.leitura import Leitura, PhNivel, BoiaNivel, UmidadeNivel
from backend.app.models.local import Local
from backend.app.models.usuario import Usuario
from backend.app.schemas.leitura import LeituraPayload
from .regra_alerta import get_regras_alerta_violadas
from .notificacao import create_notificacao
from ..schemas.notificacao import NotificacaoCreate
from ..utils.email_alertas import send_alerta_violacao_regra

def create_leitura_from_payload(db: Session, *, payload: LeituraPayload) -> None:
    """
    Creates Leitura, PhNivel, BoiaNivel, and optionally UmidadeNivel records from a payload.
    """
    local = db.query(Local).filter(Local.id == payload.dispositivo_id).first()
    if not local:
        local = db.query(Local).filter(Local.id == 1).first()
        if not local:
            raise HTTPException(status_code=404, detail=f"Local with id {payload.dispositivo_id} not found and default local with id 1 also not found.")

    # Create Leitura for pH
    leitura_ph = Leitura(
        local_id=local.id,
        sensor_tipo='PH'
    )
    db.add(leitura_ph)
    db.flush()  # Flush to get the ID for leitura_ph

    ph_nivel = PhNivel(
        leitura_id=leitura_ph.id,
        ph=payload.ph
    )
    db.add(ph_nivel)

    # Create Leitura for Boia
    leitura_boia = Leitura(
        local_id=local.id,
        sensor_tipo='BOIA'
    )
    db.add(leitura_boia)
    db.flush()  # Flush to get the ID for leitura_boia

    boia_nivel = BoiaNivel(
        leitura_id=leitura_boia.id,
        valor=payload.boia,
        status=payload.status_boia.upper()
    )
    db.add(boia_nivel)

    # Create Leitura for Umidade if data is present
    if payload.umidade_raw is not None and payload.umidade_percentual is not None and payload.umidade_status is not None:
        leitura_umidade = Leitura(
            local_id=local.id,
            sensor_tipo='UMIDADE'
        )
        db.add(leitura_umidade)
        db.flush()

        umidade_nivel = UmidadeNivel(
            leitura_id=leitura_umidade.id,
            raw=payload.umidade_raw,
            umidade_percentual=payload.umidade_percentual,
            status=payload.umidade_status.upper()
        )
        db.add(umidade_nivel)

    # Consolidate data for alert checking
    leitura_dados = {
        'ph': payload.ph,
        'valor': payload.boia,
    }
    if payload.umidade_percentual is not None:
        leitura_dados['umidade_percentual'] = payload.umidade_percentual

    # Check for violated alert rules
    regras_violadas = get_regras_alerta_violadas(db, local.id, leitura_dados)

    for regra in regras_violadas:
        # Determine the alert message
        mensagem = regra.mensagem_alerta or f"Regra de alerta violada: {regra.campo_sensor} {regra.operador} {regra.valor_limite} no local {local.nome}"
        
        # Get user info for email sending
        usuario = db.query(Usuario).filter(Usuario.email == regra.usuario_email).first()
        if usuario:
            # Send alert email
            descricao_regra = f"{regra.campo_sensor} {regra.operador} {regra.valor_limite}"
            valor_atual = leitura_dados.get(regra.campo_sensor)
            
            send_alerta_violacao_regra(
                email_to=regra.usuario_email,
                nome_usuario=usuario.nome,
                nome_sensor=local.nome,
                descricao_regra=descricao_regra,
                valor_atual=valor_atual,
                mensagem_alerta=regra.mensagem_alerta
            )
        
        # Create notification for the user who created the rule
        notificacao_data = NotificacaoCreate(
            mensagem=mensagem,
            local_id=local.id,
            email_usuario=regra.usuario_email,
            tipo="ALERTA_USUARIO"
        )
        create_notificacao(db, notificacao_data)
    
    db.commit()