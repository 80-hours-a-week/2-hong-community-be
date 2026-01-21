from database import users_db
from fastapi import HTTPException, status, UploadFile
from auth.auth_utils import verify_password, get_password_hash
import os
import shutil

UPLOAD_DIR = "public/image/profile"

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

def delete_user(user_id: int):
    users = users_db.get_users()
    initial_count = len(users)
    users = [u for u in users if u["id"] != user_id]
    
    if len(users) == initial_count:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="USER_NOT_FOUND")
        
    users_db.save_users(users)
    return True

def upload_profile_image(user_id: int, file: UploadFile):
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    
    # Simple extension check
    filename = file.filename
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    if ext not in ["jpg", "jpeg", "png"]:
         # Using 400 for invalid file type to use generic error handler
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="INVALID_FILE")

    # Rename file to user_id.ext to avoid collisions and keep it simple
    saved_filename = f"{user_id}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, saved_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # In a real app, this would be a full URL. For now, relative path.
    # Assuming the app serves /public at root or similar.
    # Reference example: "{BE-API-URL}/public/image/profile/test.jpg"
    profile_image_url = f"/public/image/profile/{saved_filename}"
    
    # Update user profile
    users = users_db.get_users()
    user_idx = -1
    for i, u in enumerate(users):
        if u["id"] == user_id:
            user_idx = i
            break
            
    if user_idx != -1:
        users[user_idx]["profileImageUrl"] = profile_image_url
        users_db.save_users(users)
        
    return profile_image_url