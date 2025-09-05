from .usuario import Usuario
from .admin import Admin
from .local import Local, PhNivel, NivelAgua
from .notificacao import Notificacao, NotificacaoAdmin
from .usuario_sensor import UsuarioSensor  # Adicione esta linha

__all__ = [
    "Usuario", "Admin", "Local", "PhNivel", "NivelAgua",
    "Notificacao", "NotificacaoAdmin", "UsuarioSensor"  # Adicione aqui também
]