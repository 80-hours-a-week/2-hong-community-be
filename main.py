from fastapi import FastAPI
from routers.user_router import router as user_router

app = FastAPI()

# GET 요청
@app.get("/hello")
def hello():
    return {"message": "Hello, FastAPI!"}

app.include_router(user_router)