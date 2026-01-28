from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    nickname = Column(String(50), unique=True, index=True, nullable=False)
    profileImageUrl = Column(String(255), nullable=True)
    createdAt = Column(DateTime, default=datetime.now)

    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")

class Post(Base):
    __tablename__ = "posts"

    postId = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    likeCount = Column(Integer, default=0)
    commentCount = Column(Integer, default=0)
    hits = Column(Integer, default=0)
    fileUrl = Column(String(255), nullable=True)
    createdAt = Column(DateTime, default=datetime.now)
    
    authorId = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = "comments"

    commentId = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    createdAt = Column(DateTime, default=datetime.now)

    authorId = Column(Integer, ForeignKey("users.id"))
    postId = Column(Integer, ForeignKey("posts.postId"))

    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
