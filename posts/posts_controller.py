from datetime import datetime
from database import posts_db
from schemas import Post, PostCreate, PostUpdate
from fastapi import HTTPException, status, Request, UploadFile
from exceptions import not_found_exception_handler
import os
import shutil
import uuid

UPLOAD_DIR = "public/image/posts"

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

def create_post(post_data: PostCreate, user: dict):
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
            "userId": user["id"],
            "nickname": user["nickname"],
            "profileImageUrl": user.get("profileImageUrl") or "http://default-image.com/profile.jpg"
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

def update_post(postId: int, post_data: PostUpdate, user: dict):
    posts = posts_db.get_posts()
    post = next((p for p in posts if p["postId"] == postId), None)
    
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POST_NOT_FOUND")
    
    if post["author"]["userId"] != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
    
    post["title"] = post_data.title
    post["content"] = post_data.content
    
    if post_data.fileUrl is not None:
        if post.get("file"):
            post["file"]["fileUrl"] = post_data.fileUrl
        else:
            post["file"] = {
                "fileId": 1,
                "fileUrl": post_data.fileUrl
            }
            
    posts_db.save_posts(posts)
    
    return {
        "code": "POST_UPDATED",
        "data": None
    }

def delete_post(postId: int, user: dict):
    posts = posts_db.get_posts()
    post = next((p for p in posts if p["postId"] == postId), None)
    
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POST_NOT_FOUND")
    
    if post["author"]["userId"] != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
    
    posts = [p for p in posts if p["postId"] != postId]
    posts_db.save_posts(posts)
    
    return {
        "code": "POST_DELETED",
        "data": None
    }

def like_post(postId: int, user: dict):
    posts = posts_db.get_posts()
    post = next((p for p in posts if p["postId"] == postId), None)
    
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POST_NOT_FOUND")
    
    if "likedBy" not in post:
        post["likedBy"] = []
    
    if user["id"] in post["likedBy"]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="POST_ALREADY_LIKED")
    
    post["likedBy"].append(user["id"])
    post["likeCount"] += 1
    
    posts_db.save_posts(posts)
    
    return {
        "code": "POST_LIKE_CREATED",
        "data": {
            "likeCount": post["likeCount"]
        }
    }

def unlike_post(postId: int, user: dict):
    posts = posts_db.get_posts()
    post = next((p for p in posts if p["postId"] == postId), None)
    
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POST_NOT_FOUND")
    
    if "likedBy" not in post:
        post["likedBy"] = []
    
    if user["id"] not in post["likedBy"]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="POST_ALREADY_UNLIKED")
    
    post["likedBy"].remove(user["id"])
    if post["likeCount"] > 0:
        post["likeCount"] -= 1
    
    posts_db.save_posts(posts)
    
    return {
        "code": "POST_LIKE_DELETED",
        "data": {
            "likeCount": post["likeCount"]
        }
    }

def upload_post_image(file: UploadFile):
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
        
    filename = file.filename
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    if ext not in ["jpg", "jpeg", "png"]:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="INVALID_FILE")
    
    saved_filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, saved_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    post_file_url = f"/public/image/posts/{saved_filename}"
    
    return {
        "code": "POST_FILE_UPLOADED",
        "data": {
            "postFileUrl": post_file_url
        }
    }
