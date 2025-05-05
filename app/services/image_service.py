from fastapi import UploadFile
import os
import uuid
from PIL import Image
import shutil

class ImageService:
    UPLOAD_DIR = "uploads"
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
    MAX_SIZE = 5 * 1024 * 1024  # 5MB

    @staticmethod
    async def save_image(file: UploadFile) -> str:
        """
        Guarda una imagen y retorna su URL relativa
        """
        # Verificar extensión
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ImageService.ALLOWED_EXTENSIONS:
            raise ValueError("Tipo de archivo no permitido")

        # Generar nombre único
        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(ImageService.UPLOAD_DIR, filename)

        # Guardar archivo
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Optimizar imagen
        try:
            with Image.open(filepath) as img:
                # Redimensionar si es muy grande
                if img.size[0] > 1920 or img.size[1] > 1080:
                    img.thumbnail((1920, 1080))
                # Guardar con compresión
                img.save(filepath, optimize=True, quality=85)
        except Exception:
            # Si falla la optimización, mantener el archivo original
            pass

        return f"/uploads/{filename}"

    @staticmethod
    async def delete_image(image_path: str) -> bool:
        """
        Elimina una imagen del sistema de archivos
        """
        if not image_path:
            return True

        # Obtener ruta real del archivo
        filepath = image_path.replace("/uploads/", "")
        full_path = os.path.join(ImageService.UPLOAD_DIR, filepath)

        try:
            if os.path.exists(full_path):
                os.remove(full_path)
            return True
        except Exception:
            return False 