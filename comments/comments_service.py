from sqlalchemy.orm import Session
from sqlalchemy import desc
from models import Comment, Post
from schemas import CommentCreate, CommentUpdate

def get_comments(postId: int, db: Session):
    return db.query(Comment).filter(Comment.post_id == postId).order_by(desc(Comment.created_at)).all()

def get_comment(commentId: int, db: Session):
    return db.query(Comment).filter(Comment.id == commentId).first()

def create_comment(postId: int, comment_data: CommentCreate, user: dict, db: Session):
    new_comment = Comment(
        post_id=postId,
        comment=comment_data.content,
        nickname=user["nickname"]
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

def update_comment(commentId: int, comment_data: CommentUpdate, db: Session):
    comment = db.query(Comment).filter(Comment.id == commentId).first()
    if comment:
        comment.comment = comment_data.content
        db.commit()
        db.refresh(comment)
    return comment

def delete_comment(commentId: int, db: Session):
    comment = db.query(Comment).filter(Comment.id == commentId).first()
    if comment:
        db.delete(comment)
        db.commit()
    return comment
