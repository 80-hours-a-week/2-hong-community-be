from sqlalchemy.orm import Session
from sqlalchemy import desc
from models import Post, Like, View, User
from posts import posts_schemas
from datetime import datetime

def get_all_posts(page: int, size: int, db: Session):
    offset = (page - 1) * size
    posts = db.query(Post).order_by(desc(Post.created_at)).offset(offset).limit(size).all()
    return posts

def get_post_detail(postId: int, db: Session):
    post = db.query(Post).filter(Post.id == postId).first()
    return post

def increase_view_count(postId: int, user_id: int, db: Session):

    existing_view = db.query(View).filter(View.post_id == postId, View.user_id == user_id).first()
    
    if not existing_view:
        new_view = View(post_id=postId, user_id=user_id)
        db.add(new_view)
        db.commit()

def get_post_view_count(postId: int, db: Session) -> int:
    return db.query(View).filter(View.post_id == postId).count()

def create_post(post_data: posts_schemas.PostCreate, user_id: int, db: Session):
    new_post = Post(
        user_id=user_id,
        title=post_data.title,
        detail=post_data.content,
        nickname=post_data.nickname, 
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

    existing_like = db.query(Like).filter(Like.post_id == postId, Like.user_id == user_id).first()
    if existing_like:
        return False
    
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
