from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from users.users_service import get_user_by_id, update_user as service_update_user, update_user_password as service_update_password, delete_user as service_delete_user, upload_profile_image as service_upload_image
from users.users_schemas import UserUpdate, UserPasswordUpdate

def get_user_info(user_id: int, current_user: dict, db: Session):
    # Check permissions
    if current_user["id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
    
    user = get_user_by_id(user_id, db)
    
    # ORM 객체 -> 응답 스키마
    return {
        "id": user.id,
        "email": user.email,
        "nickname": user.nickname,
        "profileImageUrl": user.profile_image_url,
        "createdAt": user.created_at.isoformat() if user.created_at else ""
    }

def get_my_info(current_user: dict):
    # current_user는 이미 DB에서 조회된 정보를 담고 있는 dict (auth_dependencies 참고)
    return current_user

def update_user_info(user_id: int, update_data: UserUpdate, current_user: dict, db: Session):
    # Check permissions
    if current_user["id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
    
    service_update_user(user_id, update_data.model_dump(exclude_unset=True), db)
    return {
        "code": "USER_UPDATED",
        "data": None
    }

def update_password(user_id: int, password_data: UserPasswordUpdate, current_user: dict, db: Session):
    if current_user["id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
    
    service_update_password(user_id, password_data.password, db)
    
    return {
        "code": "USER_PASSWORD_UPDATED",
        "data": None
    }

def delete_user(user_id: int, current_user: dict, db: Session):
    if current_user["id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
    
    service_delete_user(user_id, db)
    
    return {
        "code": "USER_DELETED",
        "data": None
    }

def upload_profile_image(file: UploadFile, current_user: dict, db: Session):
    # Only for me, so no userId param in URL usually for this specific endpoint structure '/me/profile-image'
    
    image_url = service_upload_image(current_user["id"], file, db)
    
    return {
        "code": "PROFILE_IMAGE_UPLOADED",
        "data": {
            "profileImageUrl": image_url
        }
    }
