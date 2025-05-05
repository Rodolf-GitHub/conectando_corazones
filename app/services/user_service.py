from app.models.user_model import User  # Importa desde models/
from app.models.profile_model import Profile
from app.schemas.user_schema import UserCreate, SuperUserCreate, UserResponse, AllUsersResponse, UserUpdate, ChangePassword
from app.database.connection import get_db
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
import os


env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

SUPERUSER_KEY = os.getenv("SUPERUSER_KEY")
if not SUPERUSER_KEY:
    raise ValueError(f"No se pudo cargar SUPERUSER_KEY del archivo {env_path}")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_user_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()
    
    


    def create_user(self, user: UserCreate) -> UserResponse:
        # Verificar si el username ya existe
        if self.get_user_by_username(user.username):
            raise ValueError(f"El usuario con username '{user.username}' ya existe")
        
        # Verificar si el email ya existe
        if self.get_user_by_email(user.email):
            raise ValueError(f"El usuario con email '{user.email}' ya existe")
        

        
        hashed_password = pwd_context.hash(user.password)
        new_user = User(
            username=user.username,
            email=user.email,
            password=hashed_password,
            is_superuser=False
        )
        try:
            # Crear el usuario
            self.db.add(new_user)
            self.db.flush()  # Para obtener el ID del usuario
            
            # Crear el perfil automáticamente con el mismo ID
            default_profile = Profile(
                id=new_user.id,  # Usar el mismo ID que el usuario
                name=user.username,
                user_id=new_user.id
            )
            self.db.add(default_profile)
            
            self.db.commit()
            self.db.refresh(new_user)
            return UserResponse(
                id=new_user.id,
                username=new_user.username,
                email=new_user.email,
                created_at=new_user.created_at,
                updated_at=new_user.updated_at,
                is_superuser=new_user.is_superuser
            )
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Error al crear el usuario. Posible duplicado de username o email.")
        
    def create_superuser(self, user: SuperUserCreate) -> UserResponse:
        # Verificar si el username ya existe
        if self.get_user_by_username(user.username):
            raise ValueError(f"El usuario con username '{user.username}' ya existe")
        
        # Verificar si el email ya existe
        if self.get_user_by_email(user.email):
            raise ValueError(f"El usuario con email '{user.email}' ya existe")
        # Verificar si el usuario es superuser
        if user.superuser_key == SUPERUSER_KEY:
                is_superuser = True
        else:
                raise ValueError("La clave de superuser es incorrecta")

        
        hashed_password = pwd_context.hash(user.password)
        new_user = User(
            username=user.username,
            email=user.email,
            password=hashed_password,
            is_superuser=True
        )
        
        try:
            # Crear el superusuario
            self.db.add(new_user)
            self.db.flush()
            
            # Crear el perfil automáticamente con el mismo ID
            default_profile = Profile(
                id=new_user.id,  # Usar el mismo ID que el usuario
                name=user.username,
                user_id=new_user.id
            )
            self.db.add(default_profile)
            
            self.db.commit()
            self.db.refresh(new_user)
            return UserResponse(
                id=new_user.id,
                username=new_user.username,
                email=new_user.email,
                created_at=new_user.created_at,
                updated_at=new_user.updated_at,
                is_superuser=new_user.is_superuser
            )
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Error al crear el usuario. Posible duplicado de username o email.")
    
    def get_user_by_id(self, user_id: str) -> UserResponse:
        """Obtiene un usuario por ID desde la base de datos"""
        db_user = self.db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise ValueError("Usuario no encontrado")

        return UserResponse(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
            is_superuser=db_user.is_superuser
        )
    
    def get_all_users(self) -> list[AllUsersResponse]:
        """Obtiene todos los usuarios desde la base de datos"""
        db_users = self.db.query(User).all()
        return [AllUsersResponse.from_orm(user) for user in db_users]

    def update_user(self, user_id: str, user_data: UserUpdate) -> User:
        # Primero verificamos si el usuario existe
        db_user = self.db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise ValueError(f"Usuario con id {user_id} no encontrado")
        
        # Si se va a actualizar el username, verificar que no exista
        if user_data.username and user_data.username != db_user.username:
            existing_user = self.db.query(User).filter(User.username == user_data.username).first()
            if existing_user:
                raise ValueError(f"El username {user_data.username} ya está en uso")
        
        # Si se va a actualizar el email, verificar que no exista
        if user_data.email and user_data.email != db_user.email:
            existing_user = self.db.query(User).filter(User.email == user_data.email).first()
            if existing_user:
                raise ValueError(f"El email {user_data.email} ya está en uso")
        
        # Actualizar los campos que vienen en la petición
        if user_data.username:
            db_user.username = user_data.username
        if user_data.email:
            db_user.email = user_data.email
        
        try:
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Error al actualizar el usuario")
    
    def change_password(self, user_id: str, password_data: ChangePassword) -> User:
        # Primero verificamos si el usuario existe
        db_user = self.db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise ValueError(f"Usuario con id {user_id} no encontrado")
        # Verificar que la contraseña actual sea correcta
        if not pwd_context.verify(password_data.old_password, db_user.password):
            raise ValueError("La contraseña actual es incorrecta")
        # Hashear y guardar la nueva contraseña
    # Hashear y guardar la nueva contraseña
        db_user.password = pwd_context.hash(password_data.new_password)
    
        try:
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except Exception:
            self.db.rollback()
            raise ValueError("Error al cambiar la contraseña")

    def delete_user(self, user_id: str) -> bool:
        try:
            # Obtener el usuario
            db_user = self.db.query(User).filter(User.id == user_id).first()
            if not db_user:
                raise ValueError("Usuario no encontrado")

            # El perfil se eliminará automáticamente debido a la relación CASCADE en la base de datos
            self.db.delete(db_user)
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Error al eliminar el usuario: {str(e)}")
                

