from datetime import datetime
from database import posts_db, comments_db
from schemas import Comment, CommentCreate, CommentUpdate
from fastapi import HTTPException, status

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
