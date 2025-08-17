from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Sensorium UFRPE"

    # Configuração de CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost", "http://localhost:8000", "http://127.0.0.1", "http://127.0.0.1:8000"]
    
    # Configurações do banco de dados
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_DATABASE: str = "banco_de_dados"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
    
    # Configuração JWT
    SECRET_KEY: str = "sua_chave_secreta_aqui"  # Em produção, use uma chave segura
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 dias
    
    # URL base
    BASE_URL: str = "http://localhost:8000"
    
    # Ambiente
    ENVIRONMENT: str = "development"
    
    class Config:
        case_sensitive = True

settings = Settings()
