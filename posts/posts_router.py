from fastapi import APIRouter, Query, Request, Depends
from models import PostCreate, PostUpdate
from posts import posts_controller
from exceptions import validation_exception_handler
from auth.auth_dependencies import get_current_user

router = APIRouter(
    prefix="/v1/posts",
    tags=["posts"]
)

@router.get("")
async def get_posts(request: Request, page: int = Query(1), size: int = Query(10)):
    if page <= 0 or size <= 0:
        return await validation_exception_handler(request, None)

    # 컨트롤러 함수 호출
    result = posts_controller.get_all_posts(page, size)
    return result

@router.get("/{postId}")
async def get_post_detail(request: Request, postId: int):
    # 컨트롤러에서 데이터 가져오기
    post = await posts_controller.get_post_detail(request, postId)
    
    return {
        "code": "post_retrieved",
        "data": post
    }

@router.post("", status_code=201)
async def create_post(post_data: PostCreate, user: dict = Depends(get_current_user)):
    return posts_controller.create_post(post_data, user)

@router.patch("/{postId}")
async def update_post(postId: int, post_data: PostUpdate, user: dict = Depends(get_current_user)):
    return posts_controller.update_post(postId, post_data, user)

@router.delete("/{postId}")
async def delete_post(postId: int, user: dict = Depends(get_current_user)):
    return posts_controller.delete_post(postId, user)

@router.post("/{postId}/likes", status_code=201)
async def like_post(postId: int, user: dict = Depends(get_current_user)):
    return posts_controller.like_post(postId, user)
