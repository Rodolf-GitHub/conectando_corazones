from app.models.user_model import User
from app.schemas.auth_schema import AuthLogin, AuthResponse
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database.connection import get_db
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import or_
from fastapi.security import OAuth2PasswordRequestForm


# Configuración para JWT
SECRET_KEY = "tu_clave_secreta_aqui"  # En producción, usar variable de entorno
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_user_by_username_or_email(self, username_or_email: str) -> User | None:
        return self.db.query(User).filter(
            or_(
                User.username == username_or_email,
                User.email == username_or_email
            )
        ).first()

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def login_oauth(self, form_data: OAuth2PasswordRequestForm) -> AuthResponse:
        """
        Método para autenticación OAuth2 (usado por Swagger/OpenAPI)
        """
        user = self.get_user_by_username_or_email(form_data.username)
        if not user:
            raise ValueError("Credenciales incorrectas")
        
        if not self.verify_password(form_data.password, user.password):
            raise ValueError("Credenciales incorrectas")
        
        # Asegurarnos de incluir el ID en el token
        access_token = self.create_access_token(
            data={
                "sub": user.username,
                "email": user.email,
                "id": user.id  # Importante: incluir el ID
            }
        )
        
        return AuthResponse(
            id=user.id,
            access_token=access_token,
            username=user.username,
            email=user.email
        )

    def login(self, login_data: AuthLogin) -> AuthResponse:
        """
        Método para login con schema personalizado
        """
        user = self.get_user_by_username_or_email(login_data.username_or_email)
        if not user:
            raise ValueError("Credenciales incorrectas")
        
        if not self.verify_password(login_data.password, user.password):
            raise ValueError("Credenciales incorrectas")
        
        access_token = self.create_access_token(
            data={
                "sub": user.username,
                "email": user.email,
                "id": user.id
            }
        )
        
        return AuthResponse(
            id=user.id,
            access_token=access_token,
            username=user.username,
            email=user.email,
        )