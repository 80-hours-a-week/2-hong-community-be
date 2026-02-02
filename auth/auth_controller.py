from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session

from auth.auth_schemas import SignupRequest, LoginRequest
from auth import auth_service
from exceptions import validation_exception_handler

async def signup(req: SignupRequest, db: Session):
    # 이메일 중복 체크
    if auth_service.is_email_exist(req.email, db):
        return JSONResponse(
            status_code=409,
            content={"code": "EMAIL_ALREADY_EXISTS", "data": None}
        )
    
    # 닉네임 중복 체크
    if auth_service.is_nickname_exist(req.nickname, db):
        return JSONResponse(
            status_code=409,
            content={"code": "NICKNAME_ALREADY_EXISTS", "data": None}
        )

    auth_service.create_user(req, db)
    
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
                "nickname": user.nickname
            }
        }
    }

async def get_me(user: dict):
    # user는 이미 auth_dependencies에서 DB 조회를 거쳐 dict나 객체로 넘어올 것임.
    # 현재 auth_dependencies.py는 JSON을 쓰거나 아직 수정되지 않았으므로 확인 필요.
    # 일단 기존 로직(dict) 호환성을 유지하거나, 객체 속성 접근으로 변경해야 함.
    # 안전하게 dict.get()을 쓰거나 getattr()을 쓸 수 있음.
    
    # 여기서는 user가 Pydantic 모델이나 dict로 넘어온다고 가정.
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
        exc = RequestValidationError([{"loc": ["query", "email"], "msg": "Email is required"}])
        return await validation_exception_handler(request, exc)
        
    if auth_service.is_email_exist(email, db):
        return JSONResponse(
            status_code=409,
            content={"code": "EMAIL_ALREADY_EXISTS", "data": None}
        )
    
    return {"code": "EMAIL_AVAILABLE", "data": None}

async def check_nickname(request: Request, nickname: str, db: Session):
    if not nickname:
        exc = RequestValidationError([{"loc": ["query", "nickname"], "msg": "Nickname is required"}])
        return await validation_exception_handler(request, exc)

    if auth_service.is_nickname_exist(nickname, db):
        return JSONResponse(
            status_code=409,
            content={"code": "NICKNAME_ALREADY_EXISTS", "data": None}
        )
    
    return {"code": "NICKNAME_AVAILABLE", "data": None}

async def logout(request: Request):
    request.session.clear()
    return {"code": "SESSION_DELETED", "data": None}
