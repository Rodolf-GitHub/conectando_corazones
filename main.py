from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(
    title="Conectando Corazones API",
    description="API para la aplicación Conectando Corazones",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configurar CORS - DEBE IR ANTES DE CUALQUIER ROUTER
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://conectando-corazones-front.onrender.com",
        "http://localhost:5173",
        "https://conectando-corazones.onrender.com",
        "*"  # Temporalmente para debug
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Crear y montar directorio para uploads
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Incluir los routers
from app.endpoints.user_endpoints import router as user_router
from app.endpoints.auth_endpoints import router as auth_router
from app.endpoints.profile_endpoints import router as profile_router

app.include_router(user_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(profile_router, prefix="/api")

# Ruta de prueba
@app.get("/")
async def root():
    return {"status": "ok", "message": "API funcionando"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", 
                host="0.0.0.0", 
                port=port,
                proxy_headers=True,
                forwarded_allow_ips="*")