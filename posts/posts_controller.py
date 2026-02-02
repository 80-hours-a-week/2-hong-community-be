from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from posts import posts_service
from schemas import PostCreate, PostUpdate
import os
import shutil
import uuid

UPLOAD_DIR = "public/image/posts"

def get_all_posts(page: int, size: int, db: Session):
    posts = posts_service.get_all_posts(page, size, db)
    
    data = []
    for p in posts:
        like_count = posts_service.get_post_like_count(p.id, db)
        view_count = posts_service.get_post_view_count(p.id, db)
        comment_count = len(p.comments)

        data.append({
            "postId": p.id,
            "title": p.title,
            "content": p.detail,
            "likeCount": like_count,
            "commentCount": comment_count,
            "hits": view_count,
            "author": {
                "userId": p.user_id,
                "nickname": p.nickname,
                "profileImageUrl": p.user.profile_image_url if p.user else None
            },
            "file": {
                "fileId": 1, # 임시
                "fileUrl": p.post_image_url
            } if p.post_image_url else None,
            "createdAt": p.created_at.isoformat() if p.created_at else ""
        })

    return {
        "code": "posts_retrieved",
        "data": data
    }

async def get_post_detail(request, postId: int, db: Session, user: dict = None):
    post = posts_service.get_post_detail(postId, db)
    
    if post is None:
        from exceptions import not_found_exception_handler
        return await not_found_exception_handler(request)
    
    if user:
         posts_service.increase_view_count(postId, user["id"], db)

    like_count = posts_service.get_post_like_count(postId, db)
    view_count = posts_service.get_post_view_count(postId, db)
    comment_count = len(post.comments)
    is_liked = posts_service.is_liked_by_user(postId, user["id"], db) if user else False

    return {
        "postId": post.id,
        "title": post.title,
        "content": post.detail,
        "likeCount": like_count,
        "commentCount": comment_count,
        "hits": view_count,
        "author": {
            "userId": post.user_id,
            "nickname": post.nickname,
            "profileImageUrl": post.user.profile_image_url if post.user else None
        },
        "file": {
            "fileId": 1,
            "fileUrl": post.post_image_url
        } if post.post_image_url else None,
        "createdAt": post.created_at.isoformat() if post.created_at else "",
        "likedBy": [l.user_id for l in post.likes] # 성능 주의
    }

def create_post(post_data: PostCreate, user: dict, db: Session):
    new_post = posts_service.create_post(post_data, user["id"], db)
    
    return {
        "code": "post_success",
        "data": {"postId": new_post.id}
    }

def update_post(postId: int, post_data: PostUpdate, user: dict, db: Session):
    post = posts_service.get_post_detail(postId, db)
    
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POST_NOT_FOUND")
    
    if post.user_id != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
    
    posts_service.update_post(postId, post_data, db)
    
    return {
        "code": "POST_UPDATED",
        "data": None
    }

def delete_post(postId: int, user: dict, db: Session):
    post = posts_service.get_post_detail(postId, db)
    
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POST_NOT_FOUND")
    
    if post.user_id != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
    
    posts_service.delete_post(postId, db)
    
    return {
        "code": "POST_DELETED",
        "data": None
    }

def like_post(postId: int, user: dict, db: Session):
    post = posts_service.get_post_detail(postId, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POST_NOT_FOUND")

    success = posts_service.like_post(postId, user["id"], db)
    if not success:
         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="POST_ALREADY_LIKED")
    
    like_count = posts_service.get_post_like_count(postId, db)
    
    return {
        "code": "POST_LIKE_CREATED",
        "data": {
            "likeCount": like_count
        }
    }

def unlike_post(postId: int, user: dict, db: Session):
    post = posts_service.get_post_detail(postId, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POST_NOT_FOUND")

    success = posts_service.unlike_post(postId, user["id"], db)
    if not success:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="POST_ALREADY_UNLIKED")

    like_count = posts_service.get_post_like_count(postId, db)

    return {
        "code": "POST_LIKE_DELETED",
        "data": {
            "likeCount": like_count
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