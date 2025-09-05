from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Sensorium UFRPE"

    # Configuração de CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]  # Permitir todas as origens para desenvolvimento
    
    # Configurações do banco de dados
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "sensorium_db")
    # Permitir override completo via variável de ambiente DATABASE_URL (útil para testes)
    DATABASE_URL_OVERRIDE: Optional[str] = os.getenv("DATABASE_URL")
    
    @property
    def DATABASE_URL(self) -> str:
        if self.DATABASE_URL_OVERRIDE:
            return self.DATABASE_URL_OVERRIDE
        return (
            f"mysql+mysqlconnector://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@"
            f"{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            f"?auth_plugin=mysql_native_password&charset=utf8mb4"
        )
    
    # Configuração JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "sua_chave_secreta_aqui_deve_ser_bem_longa_e_segura")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 horas
    
    # URL base
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")
    
    # Ambiente
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
