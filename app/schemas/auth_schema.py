from app.schemas.base_schema import BaseConfigModel
from pydantic import Field

class AuthResponse(BaseConfigModel):
    id: str = Field(..., example="a1b2c3d4e5f6...")
    access_token: str 
    username: str = Field(..., example="admin")
    email: str = Field(..., example="admin@example.com")
    
class AuthLogin(BaseConfigModel):
    username_or_email: str = Field(..., example="admin")
    password: str =Field(..., min_length=6, example="secret123")