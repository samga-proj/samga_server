import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    DB_NAME = os.getenv("DB_NAME", "samga_db")
    SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key_change_me_in_prod")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 дней

    # 🔥 ИЗМЕНЕНИЕ: Читаем строку и разбиваем её на список ключей по запятой
    # В .env пиши: GEMINI_API_KEYS="key1,key2,key3"
    _keys_str = os.getenv("GEMINI_API_KEYS", "")
    GEMINI_API_KEYS = [k.strip() for k in _keys_str.split(",") if k.strip()]