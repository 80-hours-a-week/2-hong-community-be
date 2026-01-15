from datetime import datetime
from fastapi.responses import JSONResponse
from database import posts_db
from models import Post, PostCreate, Author, PostFile
from exceptions import not_found_exception_handler

def get_all_posts(page: int, size: int):
    posts = posts_db.get_posts()
    start = (page - 1) * size
    end = start + size
    return {
        "code": "posts_retrieved",
        "data": posts[start:end]
    }

async def get_post_detail(request, postId: int):
    posts = posts_db.get_posts()
    post = next((p for p in posts if p["postId"] == postId), None)
    
    if post is None:
        return await not_found_exception_handler(request)
    
    # 조회수 증가
    post["hits"] += 1
    posts_db.save_posts(posts)
    return post

def create_post(post_data: PostCreate):
    posts = posts_db.get_posts()
    new_id = max([p["postId"] for p in posts], default=0) + 1
    
    # 1. Post 모델 인스턴스 생성
    new_post = Post(
        postId=new_id,
        title=post_data.title,
        content=post_data.content,
        likeCount=0,
        commentCount=0,
        hits=0,
        author={
            "userId": 100,
            "nickname": post_data.nickname,
            "profileImageUrl": "http://default-image.com/profile.jpg"
        },
        file={
            "fileId": 1,
            "fileUrl": post_data.image if post_data.image else ""
        },
        createdAt=datetime.now().isoformat()
    )
    
    # 2. JSON 파일에 저장하기 위해 딕셔너리로 변환
    posts.append(new_post.model_dump()) 
    posts_db.save_posts(posts)
    
    return {
        "code": "post_success",
        "data": {"postId": new_id}
    }