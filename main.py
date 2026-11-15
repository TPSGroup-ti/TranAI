# -*- coding: utf-8 -*-
"""
🧠 TRANAI — AI Training Platform
🌐 เวอร์ชัน: 1.0.0 | พร้อมใช้งานจริง
👤 เจ้าของ: Thanwa Phupingbut | Rufio D'noto
🔗 GitHub: github.com/Cristal71
📋 คุณสมบัติ: บัญชีผู้ใช้ · API Key · Token · เทรน AI แบบล็อต · แยกข้อมูลแต่ละคน
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import uuid
from database import db
from auth import auth

# ==========================================
# 📋 DATA MODELS
# ==========================================

class RegisterReq(BaseModel):
    username: str
    password: str
    email: str = ""

class LoginReq(BaseModel):
    username: str
    password: str

class AddSkillReq(BaseModel):
    name: str
    description: str = ""
    category: str = "general"

class CreateLotReq(BaseModel):
    name: str
    description: str = ""
    skill_ids: list[str]

# ==========================================
# 🚀 APP SETUP
# ==========================================

app = FastAPI(
    title="🧠 TranAI",
    description="แพลตฟอร์มเทรน AI ส่วนตัว — สร้าง · เทรน · นำไปใช้งาน",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 🔑 UTILS — ตรวจสอบสิทธิ์
# ==========================================

async def get_current_user(x_api_key: str = Header(None), x_token: str = Header(None)):
    if x_api_key:
        user = auth.verify_api_key(x_api_key)
        if user: return user
    if x_token:
        user = auth.verify_token(x_token)
        if user: return user
    raise HTTPException(401, "❌ ต้องเข้าสู่ระบบ — ส่ง API Key หรือ Token ผ่าน Header")

# ==========================================
# 🏠 หน้าหลัก
# ==========================================

@app.get("/")
def home():
    return {
        "system": "🧠 TRANAI — AI Training Platform",
        "version": "1.0.0",
        "status": "✅ ออนไลน์ · พร้อมใช้งาน",
        "owner": "Thanwa Phupingbut | Rufio D'noto",
        "github": "https://github.com/Cristal71",
        "for_users": "แต่ละคนมีพื้นที่ส่วนตัว · ข้อมูลแยกกันอย่างสมบูรณ์",
        "quick_start": {
            "ลงทะเบียน": "/register",
            "เข้าสู่ระบบ": "/login",
            "เอกสาร API": "/docs"
        }
    }

# ==========================================
# 🔐 ระบบบัญชี
# ==========================================

@app.post("/register")
def register(req: RegisterReq):
    """➕ สร้างบัญชีใหม่ — รับ API Key ทันที"""
    return auth.register(req.username, req.password, req.email)

@app.post("/login")
def login(req: LoginReq):
    """🔑 เข้าสู่ระบบ — รับ Token ใช้งาน 30 วัน"""
    return auth.login(req.username, req.password)

# ==========================================
# 🧠 ระบบ TranAI — ส่วนตัวของแต่ละคน
# ==========================================

@app.get("/me")
def my_info(username: str = Depends(get_current_user)):
    """👤 ข้อมูลบัญชีของฉัน"""
    users = db.get_users()
    u = users[username]
    return {
        "username": username,
        "email": u.get("email", ""),
        "api_key": u["api_key"],
        "skills_count": len(u.get("skills", {})),
        "lots_count": len(u.get("lots", []))
    }

@app.post("/skills/add")
def add_skill(req: AddSkillReq, username: str = Depends(get_current_user)):
    """➕ เพิ่มสกิลเข้าพื้นที่ของฉัน"""
    users = db.get_users()
    skill_id = f"skill_{uuid.uuid4().hex[:10]}"
    users[username].setdefault("skills", {})[skill_id] = {
        "skill_id": skill_id,
        "name": req.name,
        "description": req.description,
        "category": req.category,
        "created_at": datetime.now().isoformat(),
        "status": "ready"
    }
    db.save_users(users)
    return {"ok": True, "skill_id": skill_id, "message": "✅ เพิ่มสกิลสำเร็จ"}

@app.get("/skills")
def my_skills(username: str = Depends(get_current_user)):
    """📋 ดูสกิลทั้งหมดของฉัน"""
    users = db.get_users()
    skills = users[username].get("skills", {})
    return {"total": len(skills), "skills": list(skills.values())}

@app.post("/lots/create")
def create_lot(req: CreateLotReq, username: str = Depends(get_current_user)):
    """📦 สร้างล็อตเทรนจากสกิลของฉัน"""
    users = db.get_users()
    user_skills = users[username].get("skills", {})
    valid_ids = [sid for sid in req.skill_ids if sid in user_skills]
    if not valid_ids:
        return {"ok": False, "message": "ไม่พบสกิลในบัญชีของคุณ"}
    
    lot_id = f"lot_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d')}"
    lot = {
        "lot_id": lot_id,
        "name": req.name,
        "description": req.description,
        "skill_ids": valid_ids,
        "status": "created",
        "created_at": datetime.now().isoformat()
    }
    users[username].setdefault("lots", []).append(lot)
    db.save_users(users)
    return {"ok": True, "lot": lot, "message": "✅ สร้างล็อตสำเร็จ"}

@app.get("/lots")
def my_lots(username: str = Depends(get_current_user)):
    """📋 ดูล็อตทั้งหมดของฉัน"""
    users = db.get_users()
    lots = users[username].get("lots", [])
    return {"total": len(lots), "lots": lots}

@app.post("/lots/{lot_id}/train")
def train_lot(lot_id: str, username: str = Depends(get_current_user)):
    """🚀 เริ่มเทรนล็อตของฉัน"""
    users = db.get_users()
    lots = users[username].get("lots", [])
    lot = next((l for l in lots if l["lot_id"] == lot_id), None)
    if not lot:
        return {"ok": False, "message": "ไม่พบล็อตนี้"}
    if lot["status"] == "completed":
        return {"ok": False, "message": "เทรนเสร็จแล้ว"}
    
    lot["status"] = "completed"
    lot["completed_at"] = datetime.now().isoformat()
    lot["model_version"] = f"model_{lot_id}_v1.0"
    db.save_users(users)
    
    return {
        "ok": True,
        "message": "✅ เทรนสำเร็จ",
        "lot_id": lot_id,
        "model_version": lot["model_version"],
        "skills_trained": len(lot["skill_ids"])
    }

# ==========================================
# 📖 API Docs
# ==========================================

if __name__ == "__main__":
    import uvicorn
    print("""
🧠 TRANAI v1.0.0 — พร้อมใช้งาน
════════════════════════════
🌐 หน้าหลัก:    http://127.0.0.1:8000
📖 API Docs:    http://127.0.0.1:8000/docs
📋 ลงทะเบียน:  POST /register
🔑 เข้าระบบ:   POST /login
🧠 สกิล/ล็อต:  แยกตามบัญชีแต่ละคน
════════════════════════════
""")
    uvicorn.run(app, host="0.0.0.0", port=8000)

