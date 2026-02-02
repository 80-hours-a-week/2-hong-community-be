from fastapi import APIRouter, Query, Request, Depends, UploadFile, File
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from database import get_db
from schemas import PostCreate, PostUpdate
from posts import posts_controller
from auth.auth_dependencies import get_current_user
from typing import Optional

router = APIRouter(
    prefix="/v1/posts",
    tags=["posts"]
)

@router.get("")
async def get_posts(request: Request, page: int = Query(1), size: int = Query(10), db: Session = Depends(get_db)):
    if page <= 0 or size <= 0:
        # 수동으로 유효성 검사 에러 발생
        raise RequestValidationError(
            [{"loc": ["query", "page"], "msg": "Page and size must be greater than 0", "type": "value_error.number.not_gt"}]
        )

    result = posts_controller.get_all_posts(page, size, db)
    return result

@router.get("/{postId}")
async def get_post_detail(
    request: Request, 
    postId: int, 
    db: Session = Depends(get_db),
):
    post = await posts_controller.get_post_detail(request, postId, db, user=None)
    
    return {
        "code": "post_retrieved",
        "data": post
    }

@router.post("", status_code=201)
async def create_post(post_data: PostCreate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return posts_controller.create_post(post_data, user, db)

@router.patch("/{postId}")
async def update_post(postId: int, post_data: PostUpdate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return posts_controller.update_post(postId, post_data, user, db)

@router.delete("/{postId}")
async def delete_post(postId: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return posts_controller.delete_post(postId, user, db)

@router.post("/image", status_code=201)
async def upload_post_image(postFile: UploadFile = File(...), user: dict = Depends(get_current_user)):
    # Image upload doesn't need DB
    return posts_controller.upload_post_image(postFile)

@router.post("/{postId}/likes", status_code=201)
async def like_post(postId: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return posts_controller.like_post(postId, user, db)

@router.delete("/{postId}/likes")
async def unlike_post(postId: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return posts_controller.unlike_post(postId, user, db)