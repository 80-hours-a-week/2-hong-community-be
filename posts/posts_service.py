from sqlalchemy.orm import Session
from sqlalchemy import desc
from models import Post, Like, View, User
from posts import posts_schemas
from datetime import datetime

def get_all_posts(page: int, size: int, db: Session):
    offset = (page - 1) * size
    posts = db.query(Post).order_by(desc(Post.created_at)).offset(offset).limit(size).all()
    
    # 모델 객체를 딕셔너리나 스키마 형태로 변환해야 함.
    # 하지만 컨트롤러에서 변환 로직을 두는 것이 좋을 수도 있고, 서비스에서 할 수도 있음.
    # 여기서는 ORM 객체 그대로 반환하고 컨트롤러에서 처리하도록 함.
    return posts

def get_post_detail(postId: int, db: Session):
    post = db.query(Post).filter(Post.id == postId).first()
    return post

def increase_view_count(postId: int, user_id: int, db: Session):
    # 조회수 로직: 같은 유저가 중복 조회해도 카운트가 올라가는지, 아니면 유니크 뷰인지?
    # MySQLInfo.txt의 views 테이블은 user_id와 post_id가 UNIQUE임.
    # 따라서 유니크 조회수만 카운트하거나, 단순히 hits 컬럼만 올리는 방식 중 선택.
    # 여기서는 views 테이블에 기록을 남기고 성공하면 hits를 올리는 방식.
    
    # 1. View 기록 확인
    existing_view = db.query(View).filter(View.post_id == postId, View.user_id == user_id).first()
    
    if not existing_view:
        new_view = View(post_id=postId, user_id=user_id)
        db.add(new_view)
        # 2. 게시글 hits 증가 (Post 모델에는 hits 컬럼이 없고 models.py에 정의되지 않았음... 확인 필요)
        # models.py 확인 결과: models.py에 'hits' 컬럼이 없음! 'likes', 'views' 테이블만 있고 Post 테이블 컬럼이 다름.
        # MySQLInfo.txt에는 'hits' 컬럼이 없음.
        # 하지만 models.py의 기존 코드(수정 전)에는 hits가 있었음.
        # 사용자가 제공한 MySQLInfo.txt에는 hits 컬럼이 없음.
        # 따라서 views 테이블의 count로 hits를 계산해야 함.
        db.commit()

def get_post_view_count(postId: int, db: Session) -> int:
    return db.query(View).filter(View.post_id == postId).count()

def create_post(post_data: posts_schemas.PostCreate, user_id: int, db: Session):
    new_post = Post(
        user_id=user_id,
        title=post_data.title,
        detail=post_data.content, # schema: content -> db: detail
        nickname=post_data.nickname, # user테이블에 있지만 post에도 nickname 컬럼이 있음 (반정규화?)
        post_image_url=post_data.image
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

def update_post(postId: int, post_data: posts_schemas.PostUpdate, db: Session):
    post = db.query(Post).filter(Post.id == postId).first()
    if post:
        post.title = post_data.title
        post.detail = post_data.content
        if post_data.fileUrl is not None:
             post.post_image_url = post_data.fileUrl
        db.commit()
        db.refresh(post)
    return post

def delete_post(postId: int, db: Session):
    post = db.query(Post).filter(Post.id == postId).first()
    if post:
        db.delete(post)
        db.commit()
    return post

def like_post(postId: int, user_id: int, db: Session):
    # 중복 좋아요 체크
    existing_like = db.query(Like).filter(Like.post_id == postId, Like.user_id == user_id).first()
    if existing_like:
        return False # 이미 좋아요 함
    
    new_like = Like(post_id=postId, user_id=user_id)
    db.add(new_like)
    db.commit()
    return True

def unlike_post(postId: int, user_id: int, db: Session):
    existing_like = db.query(Like).filter(Like.post_id == postId, Like.user_id == user_id).first()
    if not existing_like:
        return False
    
    db.delete(existing_like)
    db.commit()
    return True

def get_post_like_count(postId: int, db: Session) -> int:
    return db.query(Like).filter(Like.post_id == postId).count()

def is_liked_by_user(postId: int, user_id: int, db: Session) -> bool:
    return db.query(Like).filter(Like.post_id == postId, Like.user_id == user_id).first() is not None
