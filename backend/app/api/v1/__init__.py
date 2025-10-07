from fastapi import APIRouter
from backend.app.api.v1.routes.estados_luz import router as estados_luz_router

# Criar o router principal
api_router = APIRouter()

# Incluir todos os routers existentes
from backend.app.api.v1.endpoints.auth import router as auth_router
from backend.app.api.v1.endpoints.usuarios import router as usuarios_router
from backend.app.api.v1.endpoints.admin import router as admin_router
from backend.app.api.v1.endpoints.local import router as local_router
from backend.app.api.v1.endpoints.notificacoes import router as notificacoes_router
from backend.app.api.v1.endpoints.relatorios import router as relatorios_router
from backend.app.api.v1.endpoints.oauth import router as oauth_router

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(usuarios_router, prefix="/usuarios", tags=["usuarios"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
api_router.include_router(local_router, prefix="/locais", tags=["locais"])
api_router.include_router(notificacoes_router, prefix="/notificacoes", tags=["notificacoes"])
api_router.include_router(relatorios_router, prefix="/relatorios", tags=["relatorios"])
api_router.include_router(oauth_router, prefix="/oauth", tags=["oauth"])

# Incluir o novo router para estados_luz
api_router.include_router(estados_luz_router, prefix="", tags=["estados_luz"])