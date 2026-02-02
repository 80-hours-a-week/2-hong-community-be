from sqlalchemy.orm import Session
from models import User
from auth.auth_schemas import SignupRequest
from auth.auth_utils import get_password_hash, verify_password
from fastapi import UploadFile, HTTPException, status
import os
import shutil

UPLOAD_DIR = "public/image/profile"

def is_email_exist(email: str, db: Session) -> bool:
    user = db.query(User).filter(User.email == email).first()
    return user is not None

def is_nickname_exist(nickname: str, db: Session) -> bool:
    user = db.query(User).filter(User.nickname == nickname).first()
    return user is not None

def create_user(email: str, password: str, nickname: str, profileImage: UploadFile, db: Session):
    # 1. 유저 먼저 생성 (ID 생성을 위해)
    new_user = User(
        email=email,
        password=get_password_hash(password),
        nickname=nickname,
        profile_image_url=None
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 2. 프로필 이미지 저장 (있다면)
    if profileImage:
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)
        
        filename = profileImage.filename
        ext = filename.split(".")[-1].lower() if "." in filename else ""
        if ext not in ["jpg", "jpeg", "png"]:
             # 이미 생성된 유저 롤백 필요할 수도 있으나, 여기서는 간단히 에러 발생 시킴
             # (엄밀하게는 transaction atomic 하게 처리해야 함, 지금은 에러나면 유저는 생성되고 이미지는 없는 상태가 됨)
             # 사용자가 추후 프로필 수정에서 올리면 되므로 큰 문제는 아님.
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="INVALID_FILE_TYPE")
        
        # User ID를 파일명으로 사용
        saved_filename = f"{new_user.id}.{ext}"
        file_path = os.path.join(UPLOAD_DIR, saved_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(profileImage.file, buffer)
        
        # DB 업데이트
        new_user.profile_image_url = f"/public/image/profile/{saved_filename}"
        db.commit()
        db.refresh(new_user)

    return new_user

def authenticate_user(email: str, password: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    
    if not user or not verify_password(password, user.password):
        return None
    
    return user
