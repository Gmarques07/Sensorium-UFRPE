from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Sensorium UFRPE"
    
    # Configurações do banco de dados
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_DATABASE: str = "banco_de_dados"
    
    # String de conexão do banco
    DATABASE_URL: str = f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    
    # Configuração JWT
    SECRET_KEY: str = "sua_chave_secreta_aqui"  # Em produção, use uma chave segura
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 dias
    
    # URL base
    BASE_URL: str = "http://localhost:8000"
    
    class Config:
        case_sensitive = True

settings = Settings()
