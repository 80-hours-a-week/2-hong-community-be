from fastapi import Header, HTTPException, status
from typing import Optional
from jose import JWTError

from database import users_db
from auth.auth_utils import decode_access_token

async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "data": None}
        )
    
    token = authorization.split(" ")[1]
    try:
        payload = decode_access_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise ValueError("Token missing sub")
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "data": None}
        )
    
    user = users_db.find_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "data": None}
        )
    return user