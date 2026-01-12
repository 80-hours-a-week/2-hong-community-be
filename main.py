from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from routers import post_router  # 만들어둔 post 라우터 임포트

app = FastAPI()

# 라우터 등록
app.include_router(post_router.router)

# 예외 처리기
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"code": "invalid_request", "data": None}
    )

@app.get("/")
async def root():
    return {"message": "Community API Server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)