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
    
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+mysqlconnector://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?auth_plugin=mysql_native_password&charset=utf8mb4"
    
    # Configuração JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "sua_chave_secreta_aqui_deve_ser_bem_longa_e_segura")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 horas
    
    # URL base
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")
    
    # Ambiente
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Configurações de e-mail
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_PORT: Optional[int] = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    EMAILS_FROM_EMAIL: Optional[str] = os.getenv("EMAILS_FROM_EMAIL")
    EMAILS_FROM_NAME: Optional[str] = os.getenv("EMAILS_FROM_NAME", "Sensorium UFRPE")
    
    @property
    def emails_enabled(self) -> bool:
        return all([
            self.SMTP_HOST,
            self.SMTP_PORT,
            self.SMTP_USER,
            self.SMTP_PASSWORD,
            self.EMAILS_FROM_EMAIL
        ])
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
