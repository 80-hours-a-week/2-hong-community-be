from database import users_db
from auth.auth_schemas import SignupRequest
from auth.auth_utils import get_password_hash, verify_password

def is_email_exist(email: str) -> bool:
    return users_db.find_user_by_email(email) is not None

def is_nickname_exist(nickname: str) -> bool:
    return users_db.find_user_by_nickname(nickname) is not None

def create_user(req: SignupRequest):
    new_user = {
        "email": req.email,
        "password": get_password_hash(req.password),
        "nickname": req.nickname,
        "profileImageUrl": req.profileImageUrl or "{BE-API-URL}/public/image/profile/default.jpg"
    }
    users_db.add_user(new_user)

def authenticate_user(email, password):
    user = users_db.find_user_by_email(email)
    
    if not user or not verify_password(password, user["password"]):
        return None
    
    return user