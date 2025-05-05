from app.endpoints.user_endpoints import router as user_router
from app.endpoints.auth_endpoints import router as auth_router
from app.endpoints.profile_endpoints import router as profile_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Crear directorio para imágenes si no existe
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Montar directorio de archivos estáticos
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Permitir el origen de tu frontend
    allow_credentials=True,  # Permitir cookies
    allow_methods=["*"],  # Permitir todos los métodos HTTP
    allow_headers=["*"],  # Permitir todos los headers
)


app.include_router(user_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(profile_router, prefix="/api")

