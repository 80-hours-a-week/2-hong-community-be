from fastapi import APIRouter, Query, status, Request, Depends
from fastapi.responses import JSONResponse
from models import PostCreate
from controllers import post_controller as controller # 컨트롤러 임포트
from exceptions import validation_exception_handler, not_found_exception_handler
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
    result = controller.get_all_posts(page, size)
    return result

@router.get("/{postId}")
async def get_post_detail(request: Request, postId: int):
    # 컨트롤러에서 데이터 가져오기
    post = controller.get_post_detail(postId)
    
    return {
        "code": "post_retrieved",
        "data": post
    }

@router.post("", status_code=201)
async def create_post(post_data: PostCreate, user: dict = Depends(get_current_user)):
    
    return controller.create_post(post_data, user)