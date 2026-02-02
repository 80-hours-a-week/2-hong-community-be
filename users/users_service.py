from sqlalchemy.orm import Session
from models import User
from fastapi import HTTPException, status, UploadFile
from auth.auth_utils import get_password_hash
import os
import shutil

UPLOAD_DIR = "public/image/profile"

def get_user_by_id(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="USER_NOT_FOUND")
    return user

def update_user(user_id: int, update_data: dict, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="USER_NOT_FOUND")
    
    if "nickname" in update_data:
        user.nickname = update_data["nickname"]
    if "profileImageUrl" in update_data:
        user.profile_image_url = update_data["profileImageUrl"]
        
    db.commit()
    db.refresh(user)
    return user

def update_user_password(user_id: int, new_password: str, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="USER_NOT_FOUND")
    
    user.password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    return user

def delete_user(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="USER_NOT_FOUND")
        
    db.delete(user)
    db.commit()
    return True

def upload_profile_image(user_id: int, file: UploadFile, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="USER_NOT_FOUND")

    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    
    filename = file.filename
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    if ext not in ["jpg", "jpeg", "png"]:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="INVALID_FILE")

    saved_filename = f"{user.id}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, saved_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    profile_image_url = f"/public/image/profile/{saved_filename}"
    
    # DB 업데이트
    user.profile_image_url = profile_image_url
    db.commit()
    db.refresh(user)
        
    return profile_image_url
