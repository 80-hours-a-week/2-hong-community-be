from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from datetime import datetime
import json
import os
from typing import List, Optional

app = FastAPI()

# 데이터 저장 파일 경로
DB_FILE = "posts.json"

# 데이터 모델 정의
class Author(BaseModel):
    userId: int
    nickname: str
    profileImageUrl: str

class PostFile(BaseModel):
    fileId: int
    fileUrl: str

class PostCreate(BaseModel):
    nickname: str
    title: str
    content: str
    image: Optional[str] = None

class Post(BaseModel):
    postId: int
    title: str
    content: str
    likeCount: int = 0
    commentCount: int = 0
    hits: int = 0
    author: dict
    file: Optional[dict] = None
    createdAt: str

# 유틸리티: JSON 데이터 로드/저장
def load_posts():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_posts(posts):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=4)

# 예외 처리기: Postman 등에서 잘못된 형식의 요청을 보낼 경우
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"code": "invalid_request", "data": None}
    )

# 1. 게시글 목록조회 (GET /V1/posts)
@app.get("/V1/posts")
async def get_posts(page: int = Query(1), size: int = Query(10)):
    posts = load_posts()
    
    # 페이지네이션 처리
    start = (page - 1) * size
    end = start + size
    paged_posts = posts[start:end]
    
    return {
        "code": "POSTS_RETRIEVED",
        "data": paged_posts
    }

# 2. 게시글 상세조회 (GET /V1/posts/{postId})
@app.get("/V1/posts/{postId}")
async def get_post_detail(postId: int):
    posts = load_posts()
    post = next((p for p in posts if p["postId"] == postId), None)
    
    if not post:
        return JSONResponse(
            status_code=400, # 존재하지 않는 경우 400 처리 또는 커스텀 처리
            content={"code": "invalid_request", "data": None}
        )
    
    # 조회수 증가
    post["hits"] += 1
    save_posts(posts)
    
    return {
        "code": "POST_RETRIEVED",
        "data": post
    }

# 3. 게시글 추가 (POST /V1/posts)
@app.post("/V1/posts", status_code=201)
async def create_post(post_data: PostCreate):
    posts = load_posts()
    
    new_id = max([p["postId"] for p in posts], default=0) + 1
    
    # 새 게시글 객체 생성
    new_post = {
        "postId": new_id,
        "title": post_data.title,
        "content": post_data.content,
        "likeCount": 0,
        "commentCount": 0,
        "hits": 0,
        "author": {
            "userId": 100, # 임의 생성
            "nickname": post_data.nickname,
            "profileImageUrl": "http://default-image.com/profile.jpg"
        },
        "file": {
            "fileId": 1,
            "fileUrl": post_data.image if post_data.image else ""
        },
        "createdAt": datetime.now().isoformat()
    }
    
    posts.append(new_post)
    save_posts(posts)
    
    return {
        "code": "post_success",
        "data": {
            "postId": new_id
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)