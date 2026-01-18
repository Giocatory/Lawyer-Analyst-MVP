from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import search, analyze, health
import logging
from app.core.config import settings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("legal-analyst")

# Проверка конфигурации при запуске
logger.info(f"Project: {settings.PROJECT_NAME}")
logger.info(f"GEMINI_API_KEY configured: {'YES' if settings.is_gemini_configured else 'NO'}")
if settings.is_gemini_configured:
    logger.info(f"Gemini Model: {settings.GEMINI_MODEL}")
else:
    logger.warning("Gemini API не настроен. Для полного функционала добавьте действительный GEMINI_API_KEY в .env файл")

app = FastAPI(title="Юрист-Аналитик API")

# 🔥 CORS — КРИТИЧЕСКИ ВАЖНО ДЛЯ ФРОНТА
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # для разработки
    allow_credentials=True,
    allow_methods=["*"],  # разрешаем OPTIONS, POST, GET
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(analyze.router, prefix="/api")
