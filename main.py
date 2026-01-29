from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from posts import posts_router
from comments import comments_router
from auth import auth_router
from users import users_router
from exceptions import register_exception_handlers
from auth.auth_utils import SECRET_KEY

from database import engine
import models

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, max_age=3600)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",     # 모든 Origin 허용 (Credentials 포함) (개발용)
    allow_credentials=True,      # 쿠키 / 세션 / 인증 헤더 허용
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙 설정 (이미지 등)
app.mount("/public", StaticFiles(directory="public"), name="public")

# 게시글 라우터 등록
app.include_router(posts_router.router)

# 댓글 라우터 등록
app.include_router(comments_router.router)

# 인증 라우터 등록
app.include_router(auth_router.router)

# 유저 라우터 등록
app.include_router(users_router.router)

# 예외 처리기 등록
register_exception_handlers(app)

# 테이블 생성
models.Base.metadata.create_all(bind=engine)

# 루트 경로
@app.get("/")
async def root():
    return {"message": "Community API Server is running"}

# 서버 실행 (python main.py 실행 간편화)
# 완성 후 제거
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)