# backend/app/core/config.py
import os
from dotenv import load_dotenv

# Загружаем .env из корневой директории backend
load_dotenv()

class Settings:
    PROJECT_NAME = "Юрист-Аналитик"
    API_PREFIX = "/api"

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyB9Sxv_bgNMMWDlQD3HGoB0ZV3T9hpW4w0").strip()
    # ИСПРАВЛЕНО: используем правильное название модели
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{{model}}:generateContent?key={{api_key}}"
    
    @property
    def is_gemini_configured(self):
        return bool(self.GEMINI_API_KEY and self.GEMINI_API_KEY.startswith("AIza"))

settings = Settings()