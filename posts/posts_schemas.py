from pydantic import BaseModel
from typing import Optional, List

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
    likedBy: List[int] = []
