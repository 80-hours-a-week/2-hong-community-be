from datetime import datetime
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from database import posts_db, comments_db
from models import Post, PostCreate, PostUpdate, CommentCreate, CommentUpdate, Comment, Author, PostFile
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

def create_comment(postId: int, comment_data: CommentCreate, user: dict):
    posts = posts_db.get_posts()
    post = next((p for p in posts if p["postId"] == postId), None)
    
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POST_NOT_FOUND")

    comments = comments_db.get_comments()
    new_comment_id = max([c["commentId"] for c in comments], default=0) + 1
    
    new_comment = Comment(
        commentId=new_comment_id,
        postId=postId,
        content=comment_data.content,
        author={
            "userId": user["id"],
            "nickname": user["nickname"],
            "profileImageUrl": user.get("profileImageUrl") or "http://default-image.com/profile.jpg"
        },
        createdAt=datetime.now().isoformat()
    )
    
    comments.append(new_comment.model_dump())
    comments_db.save_comments(comments)
    
    # Increase comment count
    post["commentCount"] += 1
    posts_db.save_posts(posts)
    
    return {
        "code": "COMMENT_CREATED",
        "data": {
            "commentId": new_comment_id
        }
    }

def update_comment(postId: int, commentId: int, comment_data: CommentUpdate, user: dict):
    posts = posts_db.get_posts()
    post = next((p for p in posts if p["postId"] == postId), None)
    
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POST_NOT_FOUND")

    comments = comments_db.get_comments()
    comment = next((c for c in comments if c["commentId"] == commentId and c["postId"] == postId), None)
    
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="COMMENT_NOT_FOUND")

    if comment["author"]["userId"] != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
    
    comment["content"] = comment_data.content
    comments_db.save_comments(comments)
    
    return {
        "code": "COMMENT_UPDATED",
        "data": None
    }

def get_comments(postId: int):
    posts = posts_db.get_posts()
    post = next((p for p in posts if p["postId"] == postId), None)
    
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POST_NOT_FOUND")

    comments = comments_db.get_comments()
    post_comments = [c for c in comments if c["postId"] == postId]
    
    return {
        "code": "COMMENTS_RETRIEVED",
        "data": post_comments
    }

def delete_comment(postId: int, commentId: int, user: dict):
    posts = posts_db.get_posts()
    post = next((p for p in posts if p["postId"] == postId), None)
    
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POST_NOT_FOUND")

    comments = comments_db.get_comments()
    comment = next((c for c in comments if c["commentId"] == commentId and c["postId"] == postId), None)
    
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="COMMENT_NOT_FOUND")

    if comment["author"]["userId"] != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
    
    comments = [c for c in comments if not (c["commentId"] == commentId and c["postId"] == postId)]
    comments_db.save_comments(comments)
    
    # Decrease comment count
    if post["commentCount"] > 0:
        post["commentCount"] -= 1
    posts_db.save_posts(posts)
    
    return {
        "code": "COMMENT_DELETED",
        "data": None
    }