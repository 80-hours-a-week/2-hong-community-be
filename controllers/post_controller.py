from datetime import datetime
from fastapi.responses import JSONResponse
from database import load_posts, save_posts
from models import Post, PostCreate, Author, PostFile

def get_all_posts(page: int, size: int):
    posts = load_posts()
    start = (page - 1) * size
    end = start + size
    return {
        "code": "POSTS_RETRIEVED",
        "data": posts[start:end]
    }

def get_post_detail(postId: int):
    posts = load_posts()
    post = next((p for p in posts if p["postId"] == postId), None)
    
    if not post:
        return None  # Router에서 처리하도록 None 반환
    
    # 조회수 증가
    post["hits"] += 1
    save_posts(posts)
    return post

def create_post(post_data: PostCreate):
    posts = load_posts()
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
    posts.append(new_post.model_dump())
    save_posts(posts)
    
    # 2. JSON 파일에 저장하기 위해 딕셔너리로 변환
    posts.append(new_post.model_dump()) 
    save_posts(posts)
    
    return {
        "code": "post_success",
        "data": {"postId": new_id}
    }