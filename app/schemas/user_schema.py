from pydantic import  EmailStr, Field
from datetime import datetime
from typing import Optional
from app.schemas.base_schema import BaseConfigModel

# Esquema para crear un usuario (Request)
class UserCreate(BaseConfigModel):
    username: str = Field(..., min_length=3, max_length=50, example="admin")
    email: EmailStr = Field(..., example="admin@example.com")  # Valida formato email
    password: str = Field(..., min_length=6, example="secret123")

class SuperUserCreate(BaseConfigModel):
    username: str = Field(..., min_length=3, max_length=50, example="admin")
    email: EmailStr = Field(..., example="admin@example.com")  # Valida formato email
    password: str = Field(..., min_length=6, example="secret123")
    superuser_key: str  = Field(..., example="superuser_key")

# Esquema para respuesta (Response)
class UserResponse(BaseConfigModel):
    id: str = Field(..., example="a1b2c3d4e5f6...")  # UUID como string
    username: str = Field(..., example="admin")
    email: EmailStr = Field(..., example="admin@example.com")
    created_at: datetime 
    updated_at: Optional[datetime] = None  # Opcional hasta la primera actualización
    is_superuser: bool = Field(..., example=True)

class AllUsersResponse(BaseConfigModel):
    id :str = Field(..., example="a1b2c3d4e5f6...")
    username: str = Field(..., example="admin")
    email: EmailStr = Field(..., example="admin@example.com")
   

class UserUpdate(BaseConfigModel):
    username: str | None = None 
    email: EmailStr | None = None
    
class ChangePassword(BaseConfigModel):
    old_password: str = Field(..., example="secret123")
    new_password: str = Field(..., example="secret1234")



