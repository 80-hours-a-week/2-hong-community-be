from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# GET 요청
@app.get("/hello")
def hello():
    return {"message": "Hello, FastAPI!"}

# POST 요청에서 받을 데이터 모델
class User(BaseModel):
    name: str
    age: int

# POST 요청
@app.post("/users")
def create_user(user: User):
    return {
        "message": "User created successfully",
        "user": user
    }