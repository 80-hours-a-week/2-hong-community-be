from fastapi import HTTPException, status
from users.users_service import get_user_by_id, update_user, update_user_password
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
    
    update_user_password(user_id, password_data.currentPassword, password_data.password)
    
    return {
        "code": "USER_PASSWORD_UPDATED",
        "data": None
    }