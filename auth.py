# -*- coding: utf-8 -*-
"""
🔐 ระบบความปลอดภัย TranAI
- ลงทะเบียน/เข้าสู่ระบบ
- สร้าง API Key อัตโนมัติ
- ตรวจสอบสิทธิ์แยกตามผู้ใช้
"""

import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from database import db

class AuthSystem:
    def __init__(self):
        self.users = db.get_users()

    def _reload(self):
        self.users = db.get_users()

    def _save(self):
        db.save_users(self.users)

    # 🔑 สร้าง API Key
    def _generate_api_key(self) -> str:
        return f"tai_{uuid.uuid4().hex[:8]}_{uuid.uuid4().hex[:12]}"

    # 🔑 สร้าง Token
    def _generate_token(self) -> str:
        return f"tok_{uuid.uuid4().hex}"

    # ✅ ลงทะเบียน
    def register(self, username: str, password: str, email: str = "") -> dict:
        self._reload()
        if username in self.users:
            return {"ok": False, "message": "ชื่อผู้ใช้นี้มีอยู่แล้ว"}
        
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        api_key = self._generate_api_key()
        
        self.users[username] = {
            "username": username,
            "password_hash": hashed_pw,
            "email": email,
            "api_key": api_key,
            "created_at": datetime.now().isoformat(),
            "tokens": [],
            "skills": {},
            "lots": []
        }
        self._save()
        
        return {
            "ok": True,
            "message": "ลงทะเบียนสำเร็จ ✅",
            "username": username,
            "api_key": api_key
        }

    # ✅ เข้าสู่ระบบ
    def login(self, username: str, password: str) -> dict:
        self._reload()
        if username not in self.users:
            return {"ok": False, "message": "ไม่พบผู้ใช้"}
        
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        if self.users[username]["password_hash"] != hashed_pw:
            return {"ok": False, "message": "รหัสผ่านไม่ถูกต้อง"}
        
        token = self._generate_token()
        expires = (datetime.now() + timedelta(days=30)).isoformat()
        
        self.users[username]["tokens"].append({
            "token": token,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires
        })
        self._save()
        
        return {
            "ok": True,
            "message": "เข้าสู่ระบบสำเร็จ ✅",
            "username": username,
            "token": token,
            "expires_at": expires,
            "api_key": self.users[username]["api_key"]
        }

    # ✅ ตรวจสอบ API Key
    def verify_api_key(self, api_key: str) -> Optional[str]:
        self._reload()
        for user, data in self.users.items():
            if data.get("api_key") == api_key:
                return user
        return None

    # ✅ ตรวจสอบ Token
    def verify_token(self, token: str) -> Optional[str]:
        self._reload()
        for user, data in self.users.items():
            for t in data.get("tokens", []):
                if t.get("token") == token:
                    exp = t.get("expires_at")
                    if exp and datetime.now().isoformat() < exp:
                        return user
        return None

auth = AuthSystem()

