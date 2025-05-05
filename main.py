from app.endpoints.user_endpoints import router as user_router
from app.endpoints.auth_endpoints import router as auth_router
from app.endpoints.profile_endpoints import router as profile_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(
    title="Conectando Corazones API",
    description="API para la aplicación Conectando Corazones",
    version="1.0.0",
    # Configurar las rutas de documentación explícitamente
    docs_url="/api/docs",          # Cambiado de /docs a /api/docs
    redoc_url="/api/redoc",        # Cambiado de /redoc a /api/redoc
    openapi_url="/api/openapi.json" # Cambiado de /openapi.json a /api/openapi.json
)

# Crear directorio para imágenes si no existe
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Montar directorio de archivos estáticos
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://conectando-corazones-front.onrender.com",  # Tu frontend en producción
        "http://localhost:5173",  # Tu frontend en desarrollo
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP
    allow_headers=["*"],  # Permite todos los headers
    expose_headers=["*"]
)


app.include_router(user_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(profile_router, prefix="/api")

