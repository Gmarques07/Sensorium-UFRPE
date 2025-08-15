from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title="Sensorium API",
    description="API do sistema Sensorium UFRPE",
    version="1.0.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importar e incluir routers aqui
# from app.api.api_v1.endpoints import users, auth, cisterna
# app.include_router(auth.router, prefix=settings.API_V1_STR + "/auth", tags=["auth"])
# app.include_router(users.router, prefix=settings.API_V1_STR + "/users", tags=["users"])
# app.include_router(cisterna.router, prefix=settings.API_V1_STR + "/cisterna", tags=["cisterna"])
