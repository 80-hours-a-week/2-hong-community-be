from fastapi import Request, UploadFile
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session

from auth.auth_schemas import SignupRequest, LoginRequest
from auth import auth_service

async def signup(email: str, password: str, nickname: str, profileImage: UploadFile, db: Session):
    # 이메일 중복 체크
    if auth_service.is_email_exist(email, db):
        return JSONResponse(
            status_code=409,
            content={"code": "EMAIL_ALREADY_EXISTS", "data": None}
        )
    
    # 닉네임 중복 체크
    if auth_service.is_nickname_exist(nickname, db):
        return JSONResponse(
            status_code=409,
            content={"code": "NICKNAME_ALREADY_EXISTS", "data": None}
        )

    auth_service.create_user(email, password, nickname, profileImage, db)
    
    return {"code": "SIGNUP_SUCCESS", "data": None}

async def login(req: LoginRequest, request: Request, db: Session):
    user = auth_service.authenticate_user(req.email, req.password, db)
    
    if not user:
        return JSONResponse(
            status_code=401,
            content={"code": "INVALID_CREDENTIALS", "data": None}
        )
    
    # 세션 저장
    request.session["user_email"] = user.email
    
    return {
        "code": "LOGIN_SUCCESS",
        "data": {
            "user": {
                "id": user.id,
                "email": user.email,
                "nickname": user.nickname,
                "profileImageUrl": user.profile_image_url
            }
        }
    }

async def get_me(user: dict):
    return {
        "code": "AUTH_SUCCESS",
        "data": {
            "id": user.get("id"),
            "email": user.get("email"),
            "nickname": user.get("nickname"),
            "profileImageUrl": user.get("profileImageUrl")
        }
    }

async def check_email(request: Request, email: str, db: Session):
    if not email:
        raise RequestValidationError([{"loc": ["query", "email"], "msg": "Email is required", "type": "value_error.missing"}])
        
    if auth_service.is_email_exist(email, db):
        return JSONResponse(
            status_code=409,
            content={"code": "EMAIL_ALREADY_EXISTS", "data": None}
        )
    
    return {"code": "EMAIL_AVAILABLE", "data": None}

async def check_nickname(request: Request, nickname: str, db: Session):
    if not nickname:
        raise RequestValidationError([{"loc": ["query", "nickname"], "msg": "Nickname is required", "type": "value_error.missing"}])

    if auth_service.is_nickname_exist(nickname, db):
        return JSONResponse(
            status_code=409,
            content={"code": "NICKNAME_ALREADY_EXISTS", "data": None}
        )
    
    return {"code": "NICKNAME_AVAILABLE", "data": None}

async def logout(request: Request):
    request.session.clear()
    return {"code": "SESSION_DELETED", "data": None}
