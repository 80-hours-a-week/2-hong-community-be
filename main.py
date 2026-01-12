from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from routers import post_router

app = FastAPI()

# 라우터 등록
app.include_router(post_router.router)

# 예외 처리기
# 1. 필수 파라미터 누락 등 유효성 검사 실패 (400)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"code": "invalid_request", "data": None}
    )

# 2. 허용되지 않은 메소드 요청 (405)
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 405:
        return JSONResponse(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            content={"code": "METHOD_NOT_ALLOWED", "data": None}
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.detail, "data": None}
    )

# 3. 서버 내부 에러 (500)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"code": "internal_server_error", "data": None}
    )

@app.get("/")
async def root():
    return {"message": "Community API Server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)