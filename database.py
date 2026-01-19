import json
import os
from typing import List, Dict, Optional

POSTS_DB_FILE = "posts.json"

class POSTS_JSONDatabase:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def get_posts(self):
        if not os.path.exists(self.file_path):
            return []
        with open(self.file_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def save_posts(self, posts):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, indent=4)

USERS_DB_FILE = "users.json"

class USERS_JSONDatabase:
    def __init__(self, file_path: str):
        self.file_path = file_path
        if not os.path.exists(file_path):
            self._write_data({"users": []})

    def _read_data(self) -> Dict:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"users": []}

    def _write_data(self, data: Dict):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def get_users(self) -> List[Dict]:
        return self._read_data().get("users", [])

    def add_user(self, user: Dict) -> Dict:
        data = self._read_data()
        if "users" not in data:
            data["users"] = []
        
        # ID 자동 증가
        user["id"] = len(data["users"]) + 1
        data["users"].append(user)
        self._write_data(data)
        return user

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

COMMENTS_DB_FILE = "comments.json"

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

posts_db = POSTS_JSONDatabase(POSTS_DB_FILE)
users_db = USERS_JSONDatabase(USERS_DB_FILE)
comments_db = COMMENTS_JSONDatabase(COMMENTS_DB_FILE)