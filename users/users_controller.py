from fastapi import HTTPException, status, UploadFile
from users.users_service import get_user_by_id, update_user, update_user_password, delete_user as service_delete_user, upload_profile_image as service_upload_image
from users.users_schemas import UserUpdate, UserPasswordUpdate

def get_user_info(user_id: int, current_user: dict):
    # Check permissions
    if current_user["id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
    
    return get_user_by_id(user_id)

def get_my_info(current_user: dict):
    return current_user

def update_user_info(user_id: int, update_data: UserUpdate, current_user: dict):
    # Check permissions
    if current_user["id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
    
    update_user(user_id, update_data.model_dump(exclude_unset=True))
    return {
        "code": "USER_UPDATED",
        "data": None
    }

def update_password(user_id: int, password_data: UserPasswordUpdate, current_user: dict):
    if current_user["id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
    
    update_user_password(user_id, password_data.password)
    
    return {
        "code": "USER_PASSWORD_UPDATED",
        "data": None
    }

def delete_user(user_id: int, current_user: dict):
    if current_user["id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
    
    service_delete_user(user_id)
    
    return {
        "code": "USER_DELETED",
        "data": None
    }

def upload_profile_image(file: UploadFile, current_user: dict):
    # Only for me, so no userId param in URL usually for this specific endpoint structure '/me/profile-image'
    # Reference: POST /v1/users/me/profile-image
    
    image_url = service_upload_image(current_user["id"], file)
    
    return {
        "code": "PROFILE_IMAGE_UPLOADED",
        "data": {
            "profileImageUrl": image_url
        }
    }