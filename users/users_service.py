from database import users_db
from fastapi import HTTPException, status
from auth.auth_utils import verify_password, get_password_hash

def get_user_by_id(user_id: int):
    user = users_db.find_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="USER_NOT_FOUND")
    return user

def update_user(user_id: int, update_data: dict):
    users = users_db.get_users()
    user_idx = -1
    for i, u in enumerate(users):
        if u["id"] == user_id:
            user_idx = i
            break
    
    if user_idx == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="USER_NOT_FOUND")
    
    current_user = users[user_idx]
    
    # Update fields if provided
    if update_data.get("nickname"):
        current_user["nickname"] = update_data["nickname"]
    if update_data.get("profileImageUrl"):
        current_user["profileImageUrl"] = update_data["profileImageUrl"]
        
    users[user_idx] = current_user
    users_db.save_users(users)
    return current_user

def update_user_password(user_id: int, current_password: str, new_password: str):
    users = users_db.get_users()
    user_idx = -1
    for i, u in enumerate(users):
        if u["id"] == user_id:
            user_idx = i
            break
            
    if user_idx == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="USER_NOT_FOUND")
    
    current_user = users[user_idx]
    
    # Verify current password
    if not verify_password(current_password, current_user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="UNAUTHORIZED")
        
    # Update password
    current_user["password"] = get_password_hash(new_password)
    users[user_idx] = current_user
    users_db.save_users(users)
    return current_user