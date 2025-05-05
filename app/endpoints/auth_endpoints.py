from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.auth_schema import AuthResponse, AuthLogin
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/", response_model=AuthResponse)
async def login_oauth(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(AuthService)
):
    """
    Endpoint para autenticación OAuth2 (usado por Swagger/OpenAPI)
    """
    try:
        return service.login_oauth(form_data)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.post("/login", response_model=AuthResponse)
async def login(
    login_data: AuthLogin,
    service: AuthService = Depends(AuthService)
):
    """
    Endpoint personalizado para login con username/email
    """
    try:
        return service.login(login_data)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

