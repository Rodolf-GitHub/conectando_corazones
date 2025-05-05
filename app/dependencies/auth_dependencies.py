from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.services.auth_service import SECRET_KEY, ALGORITHM
from app.services.user_service import UserService
from app.models.user_model import User
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth")

# Configurar el archivo de log con ruta absoluta
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
log_file = os.path.join(BASE_DIR, "debug.log")

def write_log(message: str):
    """Función auxiliar para escribir logs en el archivo"""
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{message}\n")
    except Exception as e:
        print(f"Error escribiendo log: {str(e)}")  # Fallback a print si no se puede escribir

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(UserService)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Log del token recibido
        write_log("\n--- Nueva solicitud de autenticación ---")
        write_log(f"Token recibido: {token[:20]}...")  # Solo los primeros 20 caracteres por seguridad
        
        # Decodificar token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        write_log(f"Token decodificado (payload): {payload}")
        
        # Obtener información del token
        user_id = payload.get("id")
        username = payload.get("sub")
        write_log(f"Información extraída del token - ID: {user_id}, Username: {username}")
        
        # Obtener usuario
        if user_id:
            user = user_service.get_user_by_id(user_id)
            write_log(f"Buscando usuario por ID: {user_id}")
        elif username:
            user = user_service.get_user_by_username(username)
            write_log(f"Buscando usuario por username: {username}")
        else:
            write_log("Error: No se encontró ID ni username en el token")
            raise credentials_exception
            
        if user is None:
            write_log("Error: Usuario no encontrado en la base de datos")
            raise credentials_exception
            
        write_log(f"Usuario encontrado exitosamente - ID: {user.id}, Username: {user.username}")
        return user
        
    except JWTError as e:
        write_log(f"Error al decodificar JWT: {str(e)}")
        raise credentials_exception
    except Exception as e:
        write_log(f"Error inesperado: {str(e)}")
        raise credentials_exception

async def check_superuser_or_owner(
    current_user: User = Depends(get_current_user),
    user_id: str = None
) -> User:
    """
    Verifica si el usuario actual es superusuario o el dueño del recurso.
    Si user_id es None, solo verifica si es superusuario.
    """
    if not current_user.is_superuser and (user_id is None or current_user.id != user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción. Se requiere ser superusuario o el dueño del recurso."
        )
    return current_user

async def check_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verifica si el usuario actual es superusuario
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción. Se requiere ser superusuario."
        )
    return current_user