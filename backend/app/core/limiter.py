from fastapi import Request, HTTPException, status
import threading
import time
from typing import Callable

# Simples rate limiter em memória. Não é distribuído — adequado para deployment single-process
_storage: dict = {}
_lock = threading.Lock()

def rate_limit(max_calls: int, period_seconds: int, key_prefix: str = "rl") -> Callable:
    """Factory que retorna uma dependency do FastAPI para limitar requisições.

    Uso: Depends(rate_limit(5, 60, "login"))
    - max_calls: número máximo de requisições permitidas no período
    - period_seconds: janela em segundos
    - key_prefix: prefixo para separar limites por finalidade
    """

    def _dependency(request: Request):
        # Chave baseada no IP cliente + prefixo + path para granularidade
        client_ip = request.client.host if request.client else "unknown"
        key = f"{key_prefix}:{client_ip}:{request.url.path}"
        now = time.time()

        with _lock:
            entries = _storage.get(key, [])
            # Remove timestamps fora da janela
            window_start = now - period_seconds
            entries = [ts for ts in entries if ts > window_start]
            if len(entries) >= max_calls:
                # Excedeu
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests, please slow down."
                )
            # Registra nova tentativa
            entries.append(now)
            _storage[key] = entries

        # Dependency não precisa retornar nada
        return None

    return _dependency
