from fastapi import APIRouter, Depends, status
from users import users_controller as controller
from users.users_schemas import UserUpdate, UserPasswordUpdate
from auth.auth_dependencies import get_current_user

router = APIRouter(
    prefix="/v1/users",
    tags=["users"]
)

@router.get("/me")
async def get_my_info(user: dict = Depends(get_current_user)):
    user_info = controller.get_my_info(user)
    return {
        "code": "USER_RETRIEVED",
        "data": user_info
    }

@router.get("/{userId}")
async def get_user_info(userId: int, user: dict = Depends(get_current_user)):
    user_info = controller.get_user_info(userId, user)
    return {
        "code": "USER_RETRIEVED",
        "data": user_info
    }

@router.patch("/me")
async def update_my_info(update_data: UserUpdate, user: dict = Depends(get_current_user)):
    return controller.update_user_info(user["id"], update_data, user)

@router.patch("/{userId}")
async def update_user_info(userId: int, update_data: UserUpdate, user: dict = Depends(get_current_user)):
    return controller.update_user_info(userId, update_data, user)

@router.patch("/{userId}/password")
async def update_user_password(userId: int, password_data: UserPasswordUpdate, user: dict = Depends(get_current_user)):
    return controller.update_password(userId, password_data, user)

@router.patch("/password")
async def update_my_password(password_data: UserPasswordUpdate, user: dict = Depends(get_current_user)):
    return controller.update_password(user["id"], password_data, user)

@router.delete("/me")
async def delete_me(user: dict = Depends(get_current_user)):
    return controller.delete_user(user["id"], user)

@router.delete("/{userId}")
async def delete_user(userId: int, user: dict = Depends(get_current_user)):
    return controller.delete_user(userId, user)