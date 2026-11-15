# -*- coding: utf-8 -*-
"""
💾 ฐานข้อมูลระบบ TranAI
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class Database:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.users_file = self.data_dir / "users.json"
        self.skills_file = self.data_dir / "skills.json"
        self.lots_file = self.data_dir / "lots.json"
        self._init_files()

    def _init_files(self):
        for f in [self.users_file, self.skills_file, self.lots_file]:
            if not f.exists():
                with open(f, "w", encoding="utf-8") as fp:
                    json.dump({}, fp)

    def _read(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, file_path, data):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # 📋 ผู้ใช้
    def get_users(self) -> Dict: return self._read(self.users_file)
    def save_users(self, data: Dict): self._write(self.users_file, data)

    # 📋 สกิล
    def get_skills(self) -> Dict: return self._read(self.skills_file)
    def save_skills(self, data: Dict): self._write(self.skills_file, data)

    # 📋 ล็อตเทรน
    def get_lots(self) -> Dict: return self._read(self.lots_file)
    def save_lots(self, data: Dict): self._write(self.lots_file, data)

db = Database()

