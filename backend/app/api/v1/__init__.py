from fastapi import APIRouter

# Criar o router principal
api_router = APIRouter()

# Incluir todos os routers existentes
from .endpoints.auth import router as auth_router
from .endpoints.usuarios import router as usuarios_router
from .endpoints.admin import router as admin_router
from .endpoints.local import router as local_router
from .endpoints.notificacoes import router as notificacoes_router
from .endpoints.relatorios import router as relatorios_router
from .endpoints.oauth import router as oauth_router
from .endpoints.leituras import router as leituras_router
from .endpoints.regra_alerta import router as regra_alerta_router
from .endpoints.sensor_registro import router as sensor_registro_router
print("leituras_router imported")

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(usuarios_router, prefix="/usuarios", tags=["usuarios"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
api_router.include_router(local_router, prefix="/locais", tags=["locais"])
api_router.include_router(notificacoes_router, prefix="/notificacoes", tags=["notificacoes"])
api_router.include_router(relatorios_router, prefix="/relatorios", tags=["relatorios"])
api_router.include_router(oauth_router, prefix="/oauth", tags=["oauth"])
api_router.include_router(leituras_router, prefix="/leituras", tags=["leituras"])
api_router.include_router(regra_alerta_router, prefix="/regras-alerta", tags=["regras-alerta"])
api_router.include_router(sensor_registro_router, prefix="/sensores", tags=["sensores"])







