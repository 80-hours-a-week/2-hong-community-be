from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from comments import comments_service
from posts import posts_service
from schemas import CommentCreate, CommentUpdate

def create_comment(postId: int, comment_data: CommentCreate, user: dict, db: Session):
    # 게시글 존재 여부 확인
    post = posts_service.get_post_detail(postId, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POST_NOT_FOUND")

    new_comment = comments_service.create_comment(postId, comment_data, user, db)
    
    return {
        "code": "COMMENT_CREATED",
        "data": {
            "commentId": new_comment.id
        }
    }

def update_comment(postId: int, commentId: int, comment_data: CommentUpdate, user: dict, db: Session):
    # 게시글 존재 여부 확인
    post = posts_service.get_post_detail(postId, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POST_NOT_FOUND")

    comment = comments_service.get_comment(commentId, db)
    
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="COMMENT_NOT_FOUND")

    # 댓글 작성자 확인 (user_id 비교)
    if comment.user_id != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
    
    comments_service.update_comment(commentId, comment_data, db)
    
    return {
        "code": "COMMENT_UPDATED",
        "data": None
    }

def get_comments(postId: int, db: Session):
    # 게시글 존재 여부 확인
    post = posts_service.get_post_detail(postId, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POST_NOT_FOUND")

    comments = comments_service.get_comments(postId, db)
    
    # 응답 포맷 변환
    data = []
    for c in comments:
        # c.user는 relationship으로 가져온 User 객체
        author_id = c.user.id if c.user else 0
        author_profile = c.user.profile_image_url if c.user else None
        
        data.append({
            "commentId": c.id,
            "postId": c.post_id,
            "content": c.comment,
            "author": {
                "userId": author_id,
                "nickname": c.nickname,
                "profileImageUrl": author_profile
            },
            "createdAt": c.created_at.isoformat() if c.created_at else ""
        })

    return {
        "code": "COMMENTS_RETRIEVED",
        "data": data
    }

def delete_comment(postId: int, commentId: int, user: dict, db: Session):
    # 게시글 존재 여부 확인
    post = posts_service.get_post_detail(postId, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POST_NOT_FOUND")

    comment = comments_service.get_comment(commentId, db)
    
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="COMMENT_NOT_FOUND")

    if comment.user_id != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
    
    comments_service.delete_comment(commentId, db)
    
    return {
        "code": "COMMENT_DELETED",
        "data": None
    }