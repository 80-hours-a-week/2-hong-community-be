from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas import CommentCreate, CommentUpdate
from comments import comments_controller
from auth.auth_dependencies import get_current_user

router = APIRouter(
    tags=["comments"]
)

@router.get("/{postId}/comments")
async def get_comments(postId: int, db: Session = Depends(get_db)):
    # comments 조회는 로그인 불필요? 기존 코드에서는 user=Depends(get_current_user)가 있었으나
    # 조회 자체에 유저 정보가 쓰이지 않았음 (controller.get_comments).
    # 따라서 누구나 볼 수 있게 user 의존성 제거.
    return comments_controller.get_comments(postId, db)

@router.post("/{postId}/comments", status_code=201)
async def create_comment(postId: int, comment_data: CommentCreate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return comments_controller.create_comment(postId, comment_data, user, db)

@router.patch("/{postId}/comments/{commentId}")
async def update_comment(postId: int, commentId: int, comment_data: CommentUpdate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return comments_controller.update_comment(postId, commentId, comment_data, user, db)

@router.delete("/{postId}/comments/{commentId}")
async def delete_comment(postId: int, commentId: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return comments_controller.delete_comment(postId, commentId, user, db)