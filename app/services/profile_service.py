from fastapi import Depends, UploadFile
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.profile_model import Profile
from app.models.user_model import User
from app.schemas.profile_schema import ProfileUpdate
from app.services.image_service import ImageService
from typing import List
import os
import uuid
from PIL import Image
import shutil
import logging

logger = logging.getLogger("app")

class ProfileService:
    UPLOAD_DIR = "uploads"
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
    MAX_SIZE = 5 * 1024 * 1024  # 5MB

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        # Crear directorio de uploads si no existe
        if not os.path.exists(self.UPLOAD_DIR):
            os.makedirs(self.UPLOAD_DIR)

    def get_all_profiles(self) -> List[Profile]:
        return self.db.query(Profile).all()

    def get_profile_by_user_id(self, user_id: str) -> Profile:
        """
        Obtiene un perfil por el ID del usuario
        """
        logger.info(f"Buscando perfil para user_id: {user_id}")
        
        # Intentar encontrar el perfil por user_id
        profile = self.db.query(Profile).filter(Profile.user_id == user_id).first()
        
        if profile:
            logger.info(f"Perfil encontrado - ID: {profile.id}, User ID: {profile.user_id}, Name: {profile.name}")
        else:
            # Si no se encuentra, intentar por ID
            profile = self.db.query(Profile).filter(Profile.id == user_id).first()
            if profile:
                logger.info(f"Perfil encontrado por ID - ID: {profile.id}, User ID: {profile.user_id}, Name: {profile.name}")
            else:
                logger.error(f"No se encontró perfil para el usuario {user_id}")
                # Mostrar todos los perfiles existentes
                all_profiles = self.db.query(Profile).all()
                logger.info("Perfiles existentes:")
                for p in all_profiles:
                    logger.info(f"- Profile ID: {p.id}, User ID: {p.user_id}, Name: {p.name}")
        
        if not profile:
            raise ValueError(f"No se encontró el perfil para el usuario {user_id}")
        
        return profile

    def get_profile_by_id(self, profile_id: str) -> Profile:
        profile = self.db.query(Profile).filter(Profile.id == profile_id).first()
        if not profile:
            raise ValueError(f"No se encontró el perfil con ID {profile_id}")
        return profile

    async def process_image(self, file: UploadFile) -> str:
        """
        Procesa y guarda una imagen, retornando su URL relativa
        """
        # Verificar extensión
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValueError("Tipo de archivo no permitido")

        # Generar nombre único
        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(self.UPLOAD_DIR, filename)

        # Guardar archivo
        try:
            contents = await file.read()
            with open(filepath, "wb") as buffer:
                buffer.write(contents)

            # Optimizar imagen
            with Image.open(filepath) as img:
                # Redimensionar si es muy grande
                if img.size[0] > 1920 or img.size[1] > 1080:
                    img.thumbnail((1920, 1080))
                # Guardar con compresión
                img.save(filepath, optimize=True, quality=85)
        except Exception as e:
            # Si hay error, eliminar el archivo si se creó
            if os.path.exists(filepath):
                os.remove(filepath)
            raise ValueError(f"Error al procesar la imagen: {str(e)}")

        return f"/uploads/{filename}"

    async def delete_image(self, image_path: str) -> bool:
        """
        Elimina una imagen del sistema de archivos
        """
        if not image_path or not image_path.startswith("/uploads/"):
            return True

        filepath = image_path.replace("/uploads/", "")
        full_path = os.path.join(self.UPLOAD_DIR, filepath)

        try:
            if os.path.exists(full_path):
                os.remove(full_path)
            return True
        except Exception:
            logger.error(f"Error al eliminar imagen: {full_path}")
            return False

    async def update_profile(self, profile_id: str, profile_data: ProfileUpdate) -> Profile:
        profile = self.get_profile_by_id(profile_id)
        
        # Lista de campos de imagen
        image_fields = ['cover_image', 'image_1', 'image_2', 'image_3']
        
        # Procesar cada campo
        update_data = profile_data.model_dump(exclude_unset=True)
        for field_name, value in update_data.items():
            # Si es un campo de imagen y tiene un valor nuevo
            if field_name in image_fields and value is not None:
                # Eliminar imagen anterior si existe
                old_image = getattr(profile, field_name)
                if old_image:
                    await self.delete_image(old_image)
            
            # Actualizar el campo
            setattr(profile, field_name, value)
        
        self.db.commit()
        self.db.refresh(profile)
        return profile

    async def update_profile_image(self, profile_id: str, image_type: str, file: UploadFile) -> Profile:
        """
        Actualiza una imagen del perfil (cover_image, image_1, image_2, image_3)
        """
        profile = self.db.query(Profile).filter(Profile.id == profile_id).first()
        if not profile:
            raise ValueError("Perfil no encontrado")

        # Verificar tipo de imagen válido
        valid_types = ["cover_image", "image_1", "image_2", "image_3"]
        if image_type not in valid_types:
            raise ValueError("Tipo de imagen no válido")

        # Eliminar imagen anterior si existe
        old_image = getattr(profile, image_type)
        if old_image:
            await ImageService.delete_image(old_image)

        # Guardar nueva imagen
        image_url = await ImageService.save_image(file)
        setattr(profile, image_type, image_url)

        self.db.commit()
        self.db.refresh(profile)
        return profile 