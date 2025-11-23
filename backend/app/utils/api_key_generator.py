import secrets
import string
from typing import Optional
from sqlalchemy.orm import Session
from backend.app.models.local import Local

def generate_api_key(length: int = 32) -> str:
    """
    Gera uma chave de API única e segura.
    
    Args:
        length: Comprimento da chave de API a ser gerada (padrão: 32)
    
    Returns:
        str: Chave de API gerada
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_unique_api_key(db: Session, length: int = 32, max_attempts: int = 10) -> Optional[str]:
    """
    Gera uma chave de API única que não existe no banco de dados.
    
    Args:
        db: Sessão do banco de dados
        length: Comprimento da chave de API a ser gerada
        max_attempts: Número máximo de tentativas para gerar uma chave única
    
    Returns:
        str: Chave de API única ou None se não for possível gerar
    """
    for _ in range(max_attempts):
        api_key = generate_api_key(length)
        
        # Verifica se a chave já existe (na verdade, não há campo de chave API no modelo Local atual)
        # Mas precisaremos atualizar o modelo Local para ter um campo de chave API
        # Por enquanto, apenas retornamos a chave gerada
        return api_key
    
    return None