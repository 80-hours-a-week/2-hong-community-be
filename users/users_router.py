from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
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
async def get_user_info(userId: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user_info = controller.get_user_info(userId, user, db)
    return {
        "code": "USER_RETRIEVED",
        "data": user_info
    }

@router.patch("/me")
async def update_my_info(update_data: UserUpdate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return controller.update_user_info(user["id"], update_data, user, db)

@router.patch("/password")
async def update_my_password(password_data: UserPasswordUpdate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    # Update my password
    return controller.update_password(user["id"], password_data, user, db)

@router.patch("/{userId}")
async def update_user_info(userId: int, update_data: UserUpdate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return controller.update_user_info(userId, update_data, user, db)

@router.patch("/{userId}/password")
async def update_user_password(userId: int, password_data: UserPasswordUpdate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return controller.update_password(userId, password_data, user, db)

@router.post("/me/profile-image", status_code=201)
async def upload_profile_image(profileImage: UploadFile = File(...), user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return controller.upload_profile_image(profileImage, user, db)

@router.delete("/me")
async def delete_me(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return controller.delete_user(user["id"], user, db)

@router.delete("/{userId}")
async def delete_user(userId: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return controller.delete_user(userId, user, db)
