import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# .env 파일 로드
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy 설정
# MySQL 정보가 없을 때 에러 방지를 위해 check_same_thread는 SQLite용이지만 일단 생략
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# DB 세션 의존성 주입을 위한 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 기존 JSON DB 로직 (이후 리팩토링 시 삭제 예정) ---
import json
from typing import List, Dict, Optional

class POSTS_JSONDatabase:
    def __init__(self, file_path: str):
        self.file_path = file_path
    def get_posts(self):
        if not os.path.exists(self.file_path): return []
        with open(self.file_path, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except json.JSONDecodeError: return []
    def save_posts(self, posts):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, indent=4)

class USERS_JSONDatabase:
    def __init__(self, file_path: str):
        self.file_path = file_path
        if not os.path.exists(file_path): self._write_data({"users": []})
    def _read_data(self) -> Dict:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f: return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError): return {"users": []}
    def _write_data(self, data: Dict):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    def get_users(self) -> List[Dict]: return self._read_data().get("users", [])
    def find_user_by_id(self, user_id: int) -> Optional[Dict]:
        for user in self.get_users():
            if user.get("id") == user_id: return user
        return None
    def find_user_by_email(self, email: str) -> Optional[Dict]:
        users = self.get_users()
        for user in users:
            if user.get("email") == email:
                return user
        return None
    def find_user_by_nickname(self, nickname: str) -> Optional[Dict]:
        users = self.get_users()
        for user in users:
            if user.get("nickname") == nickname:
                return user
        return None
    def add_user(self, user: Dict) -> Dict:
        data = self._read_data()
        if "users" not in data:
            data["users"] = []
        user["id"] = len(data["users"]) + 1
        data["users"].append(user)
        self._write_data(data)
        return user
    def save_users(self, users: List[Dict]): self._write_data({"users": users})

class COMMENTS_JSONDatabase:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def get_comments(self):
        if not os.path.exists(self.file_path):
            return []
        with open(self.file_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def save_comments(self, comments):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(comments, f, ensure_ascii=False, indent=4)

posts_db = POSTS_JSONDatabase("posts.json")
users_db = USERS_JSONDatabase("users.json")
comments_db = COMMENTS_JSONDatabase("comments.json")