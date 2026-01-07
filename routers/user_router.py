from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# POST 요청에서 받을 데이터 모델
class User(BaseModel):
    name: str
    age: int

# POST 요청
@router.post("/users")
def create_user(user: User):
    return {
        "message": "User created successfully",
        "user": user
    }