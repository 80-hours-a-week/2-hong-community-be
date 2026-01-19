from pydantic import BaseModel
from typing import Optional

class Author(BaseModel):
    userId: int
    nickname: str
    profileImageUrl: str

class PostFile(BaseModel):
    fileId: int
    fileUrl: str

class PostCreate(BaseModel):
    nickname: str
    title: str
    content: str
    image: Optional[str] = None

class PostUpdate(BaseModel):
    title: str
    content: str
    fileUrl: Optional[str] = None

class Post(BaseModel):
    postId: int
    title: str
    content: str
    likeCount: int = 0
    commentCount: int = 0
    hits: int = 0
    author: dict
    file: Optional[dict] = None
    createdAt: str

class CommentCreate(BaseModel):
    content: str

class CommentUpdate(BaseModel):
    content: str

class Comment(BaseModel):
    commentId: int
    postId: int
    content: str
    author: dict
    createdAt: str