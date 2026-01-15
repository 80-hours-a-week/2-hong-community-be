from fastapi import APIRouter, Depends, Request

from auth.auth_schemas import (
    SignupRequest, LoginRequest, BaseResponse, 
    LoginResponse, MeResponse
)
from auth import auth_controller
from auth.auth_dependencies import get_current_user

router = APIRouter(
    prefix="/v1/auth", 
    tags=["Auth"]
)

@router.post("/signup", status_code=201, response_model=BaseResponse)
async def signup(req: SignupRequest):
    return await auth_controller.signup(req)

@router.post("/login", status_code=200, response_model=LoginResponse)
async def login(req: LoginRequest):
    return await auth_controller.login(req)

@router.get("/me", status_code=200, response_model=MeResponse)
async def get_me(user: dict = Depends(get_current_user)):
    return await auth_controller.get_me(user)

@router.get("/emails/availability", status_code=200, response_model=BaseResponse)
async def check_email(request: Request, email: str):
    return await auth_controller.check_email(request, email)

@router.get("/nicknames/availability", status_code=200, response_model=BaseResponse)
async def check_nickname(request: Request, nickname: str):
    return await auth_controller.check_nickname(request, nickname)

@router.delete("/session", status_code=200, response_model=BaseResponse)
async def logout():
    return await auth_controller.logout()