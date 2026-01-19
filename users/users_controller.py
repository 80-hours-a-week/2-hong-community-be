from fastapi import HTTPException, status
from users.users_service import get_user_by_id, update_user
from users.users_schemas import UserUpdate

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