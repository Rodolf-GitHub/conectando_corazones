from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile, Form
from app.services.profile_service import ProfileService
from app.schemas.profile_schema import ProfileResponse, ProfileUpdate, AllProfilesResponse
from app.models.user_model import User
from app.dependencies.auth_dependencies import get_current_user, check_superuser, check_superuser_or_owner
from typing import List, Optional
from app.models.profile_model import Profile
import logging
from app.dependencies.auth_dependencies import get_current_user

# Configurar el logger
logger = logging.getLogger("app")

router = APIRouter(prefix="/profiles", tags=["profiles"])

@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    service: ProfileService = Depends(ProfileService)
):
    """
    Ruta protegida para obtener el perfil del usuario autenticado
    """
    try:
        # Solo buscar el perfil existente por user_id
        profile = service.db.query(Profile).filter(Profile.user_id == current_user.id).first()
        if not profile:
            raise ValueError(f"No se encontró el perfil para el usuario {current_user.username}")
        return profile
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("", response_model=List[AllProfilesResponse])
async def get_all_profiles(
    service: ProfileService = Depends(ProfileService)
):
    """
    Ruta pública para obtener todos los perfiles con información básica
    """
    return service.get_all_profiles()

@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: str,
    service: ProfileService = Depends(ProfileService)
):
    """
    Ruta pública para obtener los detalles de un perfil específico
    """
    try:
        return service.get_profile_by_id(profile_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/me", response_model=ProfileResponse)
async def update_my_profile(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    whatsapp_link: Optional[str] = Form(None),
    facebook_link: Optional[str] = Form(None),
    cover_image: Optional[UploadFile] = File(None),
    image_1: Optional[UploadFile] = File(None),
    image_2: Optional[UploadFile] = File(None),
    image_3: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    service: ProfileService = Depends(ProfileService)
):
    """
    Ruta protegida para actualizar el perfil propio
    """
    try:
        # Obtener el perfil existente
        profile = service.db.query(Profile).filter(Profile.user_id == current_user.id).first()
        if not profile:
            raise ValueError(f"No se encontró el perfil para el usuario {current_user.username}")
        
        # Crear objeto ProfileUpdate con los datos del formulario
        profile_data = ProfileUpdate(
            name=name,
            description=description,
            whatsapp_link=whatsapp_link,
            facebook_link=facebook_link
        )
        
        # Procesar las imágenes si se proporcionaron
        if cover_image:
            profile_data.cover_image = await service.process_image(cover_image)
        if image_1:
            profile_data.image_1 = await service.process_image(image_1)
        if image_2:
            profile_data.image_2 = await service.process_image(image_2)
        if image_3:
            profile_data.image_3 = await service.process_image(image_3)
            
        # Actualizar el perfil
        result = await service.update_profile(profile.id, profile_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: str,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    whatsapp_link: Optional[str] = Form(None),
    facebook_link: Optional[str] = Form(None),
    cover_image: Optional[UploadFile] = File(None),
    image_1: Optional[UploadFile] = File(None),
    image_2: Optional[UploadFile] = File(None),
    image_3: Optional[UploadFile] = File(None),
    service: ProfileService = Depends(ProfileService),
    current_user: User = Depends(get_current_user)
):
    """
    Ruta protegida para actualizar cualquier perfil (requiere superusuario o ser el dueño)
    """
    try:
        # Obtener el perfil para verificar el user_id
        profile = service.db.query(Profile).filter(Profile.id == profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Perfil no encontrado")
        
        # Verificar permisos
        if not current_user.is_superuser and current_user.id != profile.user_id:
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para actualizar este perfil"
            )

        # Crear objeto ProfileUpdate con los datos del formulario
        profile_data = ProfileUpdate(
            name=name,
            description=description,
            whatsapp_link=whatsapp_link,
            facebook_link=facebook_link
        )
        
        # Procesar las imágenes si se proporcionaron
        if cover_image:
            profile_data.cover_image = await service.process_image(cover_image)
        if image_1:
            profile_data.image_1 = await service.process_image(image_1)
        if image_2:
            profile_data.image_2 = await service.process_image(image_2)
        if image_3:
            profile_data.image_3 = await service.process_image(image_3)
            
        result = await service.update_profile(profile_id, profile_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

