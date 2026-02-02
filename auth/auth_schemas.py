from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Any, Dict, List

# 공통 응답 구조
class BaseResponse(BaseModel):
    code: str
    data: Any

# 회원가입
class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=20)
    nickname: str = Field(..., min_length=2, max_length=10)
    profileImageUrl: Optional[str] = None

# 로그인
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# 사용자 정보 (응답용)
class UserInfo(BaseModel):
    id: int
    email: str
    nickname: str
    profileImageUrl: Optional[str] = None

# 로그인 성공 데이터
class LoginSuccessData(BaseModel):
    user: Dict[str, Any]  # id, email, nickname 포함

# 에러 응답 데이터 구조 (422 등)
class ValidationErrorData(BaseModel):
    email: Optional[List[str]] = None
    password: Optional[List[str]] = None
    nickname: Optional[List[str]] = None
    profileImageUrl: Optional[List[str]] = None

# API 응답 모델들
class SignupResponse(BaseResponse):
    pass

class LoginResponse(BaseResponse):
    data: LoginSuccessData

class MeResponse(BaseResponse):
    data: UserInfo