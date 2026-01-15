from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Optional
from jose import JWTError

from database import users_db
from auth.auth_schemas import (
    SignupRequest, LoginRequest, BaseResponse, 
    LoginResponse, MeResponse, UserInfo
)
from auth.auth_utils import (
    get_password_hash, verify_password, create_access_token, decode_access_token
)
from exceptions import validation_exception_handler

router = APIRouter(
    prefix="/v1/auth", 
    tags=["Auth"]
)

# --- 의존성 주입 (Dependency) ---
async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, # exceptions.py에서 가져오기
            detail={"code": "UNAUTHORIZED", "data": None}
        )
    
    token = authorization.split(" ")[1]
    try:
        payload = decode_access_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise ValueError("Token missing sub")
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, # exceptions.py에서 가져오기
            detail={"code": "UNAUTHORIZED", "data": None}
        )
    
    user = users_db.find_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, # exceptions.py에서 가져오기
            detail={"code": "UNAUTHORIZED", "data": None}
        )
    return user

# --- 엔드포인트 구현 ---

@router.post("/signup", status_code=201, response_model=BaseResponse)
async def signup(req: SignupRequest):
    # 이메일 중복 체크
    if users_db.find_user_by_email(req.email):
        return JSONResponse(
            status_code=409,
            content={"code": "EMAIL_ALREADY_EXISTS", "data": None}
        )
    
    # 닉네임 중복 체크
    if users_db.find_user_by_nickname(req.nickname):
        return JSONResponse(
            status_code=409,
            content={"code": "NICKNAME_ALREADY_EXISTS", "data": None}
        )

    new_user = {
        "email": req.email,
        "password": get_password_hash(req.password),
        "nickname": req.nickname,
        "profileImageUrl": req.profileImageUrl or "{BE-API-URL}/public/image/profile/default.jpg"
    }
    
    users_db.add_user(new_user)
    
    return {"code": "SIGNUP_SUCCESS", "data": None}

@router.post("/login", status_code=200, response_model=LoginResponse)
async def login(req: LoginRequest):
    user = users_db.find_user_by_email(req.email)
    
    if not user or not verify_password(req.password, user["password"]):
        return JSONResponse(
            status_code=401,
            content={"code": "INVALID_CREDENTIALS", "data": None}
        )
    
    # 토큰 생성
    access_token = create_access_token(data={"sub": user["email"]})
    
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

@router.get("/me", status_code=200, response_model=MeResponse)
async def get_me(user: dict = Depends(get_current_user)):
    return {
        "code": "AUTH_SUCCESS",
        "data": {
            "id": user["id"],
            "email": user["email"],
            "nickname": user["nickname"],
            "profileImageUrl": user.get("profileImageUrl")
        }
    }

@router.get("/emails/availability", status_code=200, response_model=BaseResponse)
async def check_email(request: Request, email: str):
    if not email:
        exc = RequestValidationError([{"loc": ["query", "email"], "msg": "Email is required"}])
        return await validation_exception_handler(request, exc)
        
    if users_db.find_user_by_email(email):
        return JSONResponse(
            status_code=409,
            content={"code": "EMAIL_ALREADY_EXISTS", "data": None}
        )
    
    return {"code": "EMAIL_AVAILABLE", "data": None}

@router.get("/nicknames/availability", status_code=200, response_model=BaseResponse)
async def check_nickname(request: Request, nickname: str):
    if not nickname:
        exc = RequestValidationError([{"loc": ["query", "nickname"], "msg": "Nickname is required"}])
        return await validation_exception_handler(request, exc)

    if users_db.find_user_by_nickname(nickname):
        return JSONResponse(
            status_code=409,
            content={"code": "NICKNAME_ALREADY_EXISTS", "data": None}
        )
    
    return {"code": "NICKNAME_AVAILABLE", "data": None}

@router.delete("/session", status_code=200, response_model=BaseResponse)
async def logout():
    # JWT는 서버 상태가 없으므로 클라이언트에서 토큰 폐기.
    # 성공 응답만 반환.
    return {"code": "SESSION_DELETED", "data": None}