from fastapi import APIRouter, Depends, HTTPException
from app.services.user_service import UserService
from app.schemas.user_schema import UserCreate,SuperUserCreate, UserResponse,AllUsersResponse, UserUpdate, ChangePassword
from app.models.user_model import User
from app.dependencies.auth_dependencies import get_current_user, check_superuser, check_superuser_or_owner


router = APIRouter(prefix="/users", tags=["users"])

@router.post("/create_superuser", response_model=UserResponse)
async def create_superuser(
    user: SuperUserCreate,
    service: UserService = Depends(UserService)
):
    try:
        return service.create_superuser(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.post("/", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    service: UserService = Depends(UserService),
    _: User = Depends(check_superuser)  # Solo superusuario puede crear usuarios
):
    try:
        return service.create_user(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    
    user_id: str,
    service: UserService = Depends(UserService),
    current_user: User = Depends(get_current_user)
    
):
    try:
        return service.get_user_by_id(user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    
@router.get("", response_model=list[AllUsersResponse])
async def get_all_users(
    service: UserService = Depends(UserService),
    current_user: User = Depends(get_current_user)
):
    return service.get_all_users()

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    service: UserService = Depends(UserService),
    current_user: User = Depends(get_current_user)
):
    try:
        return service.update_user(user_id, user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/change_password/{user_id}", response_model=UserResponse)
async def change_password(
    user_id: str,
    password_data: ChangePassword,
    service: UserService = Depends(UserService),
    current_user: User = Depends(check_superuser_or_owner)  # Primero obtener el usuario
):
    # Verificar permisos después de tener el usuario
    await check_superuser_or_owner(current_user, user_id)
    try:
        return service.change_password(user_id, password_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    service: UserService = Depends(UserService),
    _: User = Depends(check_superuser)  # Solo superusuario puede eliminar usuarios
):
    try:
        if service.delete_user(user_id):
            return {"message": "Usuario eliminado correctamente"}
        return {"message": "Error al eliminar el usuario"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
