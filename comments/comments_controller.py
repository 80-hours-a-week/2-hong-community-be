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

    # 댓글 작성자 확인 (닉네임 비교... 하지만 닉네임 변경 가능성 때문에 ID가 안전하나 스키마 한계로 닉네임 비교)
    # ORM 모델에는 nickname만 있고 user_id가 없음.
    # 따라서 "현재 유저의 닉네임"과 "댓글 작성자 닉네임"이 같으면 권한이 있다고 간주해야 함.
    # (보안상 취약하지만 스키마 제약 따름)
    if comment.nickname != user["nickname"]:
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
        data.append({
            "commentId": c.id,
            "postId": c.post_id,
            "content": c.comment,
            "author": {
                # 스키마 한계로 userId 알 수 없음. 임시값 혹은 닉네임 조회?
                # 조회 시점의 닉네임 사용자 ID를 역추적하거나 그냥 0 또는 생략해야 함.
                # 하지만 프론트엔드 호환성을 위해 user 필드 구조 유지 필요.
                "userId": 0, # Unknown
                "nickname": c.nickname,
                "profileImageUrl": None # 알 수 없음
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

    if comment.nickname != user["nickname"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
    
    comments_service.delete_comment(commentId, db)
    
    return {
        "code": "COMMENT_DELETED",
        "data": None
    }