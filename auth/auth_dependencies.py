from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User

async def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_email = request.session.get("user_email")
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "data": None}
        )
    
    # JSON DB 대신 MySQL DB에서 조회
    user = db.query(User).filter(User.email == user_email).first()
    
    if user is None:
        # 세션은 있는데 DB에 사용자가 없는 경우 (탈퇴 등) 세션 삭제 후 에러
        request.session.clear()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "data": None}
        )
    
    # SQLAlchemy 객체는 dict처럼 사용하기 위해 속성들을 딕셔너리로 변환하거나, 
    # 혹은 객체 그대로 넘기고 사용하는 곳에서 속성으로 접근하게 함.
    # 여기서는 호환성을 위해 dict 형태로 변환하여 반환합니다.
    return {
        "id": user.id,
        "email": user.email,
        "nickname": user.nickname,
        "profileImageUrl": user.profile_image_url,
        "createdAt": user.created_at.isoformat() if user.created_at else None
    }
