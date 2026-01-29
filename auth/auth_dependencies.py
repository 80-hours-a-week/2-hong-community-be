from fastapi import Request, HTTPException, status
from database import users_db

async def get_current_user(request: Request):
    user_email = request.session.get("user_email")
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "data": None}
        )
    
    user = users_db.find_user_by_email(user_email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "data": None}
        )
    return user