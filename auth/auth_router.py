from fastapi import APIRouter, Depends, Request, Form, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
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
async def signup(
    email: str = Form(...),
    password: str = Form(...),
    nickname: str = Form(...),
    profileImage: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    return await auth_controller.signup(email, password, nickname, profileImage, db)

@router.post("/login", status_code=200, response_model=LoginResponse)
async def login(req: LoginRequest, request: Request, db: Session = Depends(get_db)):
    return await auth_controller.login(req, request, db)

@router.get("/me", status_code=200, response_model=MeResponse)
async def get_me(user: dict = Depends(get_current_user)):
    return await auth_controller.get_me(user)

@router.get("/emails/availability", status_code=200, response_model=BaseResponse)
async def check_email(request: Request, email: str, db: Session = Depends(get_db)):
    return await auth_controller.check_email(request, email, db)

@router.get("/nicknames/availability", status_code=200, response_model=BaseResponse)
async def check_nickname(request: Request, nickname: str, db: Session = Depends(get_db)):
    return await auth_controller.check_nickname(request, nickname, db)

@router.delete("/session", status_code=200, response_model=BaseResponse)
async def logout(request: Request, user: dict = Depends(get_current_user)):
    return await auth_controller.logout(request)
