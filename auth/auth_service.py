from sqlalchemy.orm import Session
from models import User
from auth.auth_schemas import SignupRequest
from auth.auth_utils import get_password_hash, verify_password

def is_email_exist(email: str, db: Session) -> bool:
    user = db.query(User).filter(User.email == email).first()
    return user is not None

def is_nickname_exist(nickname: str, db: Session) -> bool:
    user = db.query(User).filter(User.nickname == nickname).first()
    return user is not None

def create_user(req: SignupRequest, db: Session):
    new_user = User(
        email=req.email,
        password=get_password_hash(req.password),
        nickname=req.nickname,
        profile_image_url=req.profileImageUrl or "http://default-image.com/profile.jpg"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def authenticate_user(email: str, password: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    
    if not user or not verify_password(password, user.password):
        return None
    
    return user
