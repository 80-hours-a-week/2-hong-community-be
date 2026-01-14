from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from routers import post_router
from exceptions import register_exception_handlers

app = FastAPI()

# 라우터 등록
app.include_router(post_router.router)

# 예외 처리기 등록
register_exception_handlers(app)

@app.get("/")
async def root():
    return {"message": "Community API Server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)