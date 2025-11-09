from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.db.base_class import Base

class RegraAlerta(Base):
    __tablename__ = "regras_alerta"

    id = Column(Integer, primary_key=True, index=True)
    usuario_email = Column(String(100), nullable=False)  # Email do usuário dono da regra
    local_id = Column(Integer, ForeignKey("locais.id"), nullable=False)  # Local/sensor monitorado
    sensor_tipo = Column(Enum('PH', 'UMIDADE', 'BOIA', name='sensor_tipo_enum'), nullable=False)  # Tipo de sensor
    campo_sensor = Column(String(50), nullable=False)  # Campo do sensor (ex: 'ph', 'valor', 'umidade_percentual')
    operador = Column(Enum('>', '<', '>=', '<=', '==', '!=', name='operador_enum'), nullable=False)  # Operador de comparação
    valor_limite = Column(Float, nullable=False)  # Valor limite para a comparação
    mensagem_alerta = Column(Text)  # Mensagem personalizada para o alerta
    ativa = Column(Boolean, default=True)  # Flag indicando se a regra está ativa
    data_criacao = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    data_atualizacao = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relacionamentos
    local = relationship("Local", back_populates="regras_alerta")

    def to_dict(self):
        return {
            "id": self.id,
            "usuario_email": self.usuario_email,
            "local_id": self.local_id,
            "sensor_tipo": self.sensor_tipo,
            "campo_sensor": self.campo_sensor,
            "operador": self.operador,
            "valor_limite": self.valor_limite,
            "mensagem_alerta": self.mensagem_alerta,
            "ativa": self.ativa,
            "data_criacao": self.data_criacao,
            "data_atualizacao": self.data_atualizacao
        }