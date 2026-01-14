from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse
from models import PostCreate
from controllers import post_controller as controller # 컨트롤러 임포트

router = APIRouter(
    prefix="/v1/posts",
    tags=["posts"]
)

@router.get("")
async def get_posts(page: int = Query(1), size: int = Query(10)):
    # 컨트롤러 함수 호출
    result = controller.get_all_posts(page, size)
    return result

@router.get("/{postId}")
async def get_post_detail(postId: int):
    # 컨트롤러에서 데이터 가져오기
    post = controller.get_post_detail(postId)
    
    if not post:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"code": "Not_found", "data": None}
        )
    
    return {
        "code": "POST_RETRIEVED",
        "data": post
    }

@router.post("", status_code=201)
async def create_post(post_data: PostCreate):
    
    return controller.create_post(post_data)