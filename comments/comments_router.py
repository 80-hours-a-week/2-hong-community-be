from fastapi import APIRouter, Depends
from schemas import CommentCreate, CommentUpdate
from comments import comments_controller
from auth.auth_dependencies import get_current_user

router = APIRouter(
    prefix="/v1/posts",
    tags=["comments"]
)

@router.get("/{postId}/comments")
async def get_comments(postId: int, user: dict = Depends(get_current_user)):
    return comments_controller.get_comments(postId)

@router.post("/{postId}/comments", status_code=201)
async def create_comment(postId: int, comment_data: CommentCreate, user: dict = Depends(get_current_user)):
    return comments_controller.create_comment(postId, comment_data, user)

@router.patch("/{postId}/comments/{commentId}")
async def update_comment(postId: int, commentId: int, comment_data: CommentUpdate, user: dict = Depends(get_current_user)):
    return comments_controller.update_comment(postId, commentId, comment_data, user)

@router.delete("/{postId}/comments/{commentId}")
async def delete_comment(postId: int, commentId: int, user: dict = Depends(get_current_user)):
    return comments_controller.delete_comment(postId, commentId, user)
