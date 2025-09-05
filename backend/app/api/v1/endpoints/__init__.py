from .auth import router as auth_router
from .usuarios import router as usuarios_router
from .admin import router as admin_router
from .local import router as local_router
from .notificacoes import router as notificacoes_router
from .relatorios import router as relatorios_router

__all__ = [
    "auth_router",
    "usuarios_router",
    "admin_router",
    "local_router",
    "notificacoes_router",
    "relatorios_router"
]