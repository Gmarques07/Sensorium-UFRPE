from fastapi import APIRouter
from .endpoints import (
    auth_router,
    usuarios_router,
    admin_router,
    local_router,
    notificacoes_router
)

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(usuarios_router, prefix="/usuarios", tags=["usuarios"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
api_router.include_router(local_router, prefix="/local", tags=["local"])
api_router.include_router(notificacoes_router, prefix="/notificacoes", tags=["notificacoes"])
