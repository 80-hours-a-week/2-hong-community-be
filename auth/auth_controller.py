from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from auth.auth_schemas import SignupRequest, LoginRequest
from auth import auth_service
from exceptions import validation_exception_handler

async def signup(req: SignupRequest):
    # 이메일 중복 체크
    if auth_service.is_email_exist(req.email):
        return JSONResponse(
            status_code=409,
            content={"code": "EMAIL_ALREADY_EXISTS", "data": None}
        )
    
    # 닉네임 중복 체크
    if auth_service.is_nickname_exist(req.nickname):
        return JSONResponse(
            status_code=409,
            content={"code": "NICKNAME_ALREADY_EXISTS", "data": None}
        )

    auth_service.create_user(req)
    
    return {"code": "SIGNUP_SUCCESS", "data": None}

async def login(req: LoginRequest):
    user = auth_service.authenticate_user(req.email, req.password)
    
    if not user:
        return JSONResponse(
            status_code=401,
            content={"code": "INVALID_CREDENTIALS", "data": None}
        )
    
    # 토큰 생성
    access_token = auth_service.generate_access_token(user["email"])
    
    return {
        "code": "LOGIN_SUCCESS",
        "data": {
            "user": {
                "id": user["id"],
                "email": user["email"],
                "nickname": user["nickname"],
                "authToken": access_token
            }
        }
    }

async def get_me(user: dict):
    return {
        "code": "AUTH_SUCCESS",
        "data": {
            "id": user["id"],
            "email": user["email"],
            "nickname": user["nickname"],
            "profileImageUrl": user.get("profileImageUrl")
        }
    }

async def check_email(request: Request, email: str):
    if not email:
        exc = RequestValidationError([{"loc": ["query", "email"], "msg": "Email is required"}])
        return await validation_exception_handler(request, exc)
        
    if auth_service.is_email_exist(email):
        return JSONResponse(
            status_code=409,
            content={"code": "EMAIL_ALREADY_EXISTS", "data": None}
        )
    
    return {"code": "EMAIL_AVAILABLE", "data": None}

async def check_nickname(request: Request, nickname: str):
    if not nickname:
        exc = RequestValidationError([{"loc": ["query", "nickname"], "msg": "Nickname is required"}])
        return await validation_exception_handler(request, exc)

    if auth_service.is_nickname_exist(nickname):
        return JSONResponse(
            status_code=409,
            content={"code": "NICKNAME_ALREADY_EXISTS", "data": None}
        )
    
    return {"code": "NICKNAME_AVAILABLE", "data": None}

async def logout():
    return {"code": "AUTH_TOKEN_DELETED", "data": None}