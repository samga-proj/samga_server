import asyncio
import os
import sys
from google import genai

# Добавляем путь к конфигу
sys.path.append(os.getcwd())

try:
    from config import Config
except ImportError:
    Config = None


async def list_models():
    api_key = None

    # Берем ключ из конфига
    if Config and hasattr(Config, 'GEMINI_API_KEYS') and Config.GEMINI_API_KEYS:
        api_key = Config.GEMINI_API_KEYS[0]

    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("❌ Ключ не найден.")
        return

    client = genai.Client(api_key=api_key)
    print(f"🔑 Ключ: {api_key[:5]}... Сканирую модели...\n")

    try:
        # Получаем список
        models = await client.aio.models.list()

        count = 0
        for model in models:
            # Просто печатаем имя каждой найденной модели
            print(f"📦 Модель: {model.name}")
            count += 1

        if count == 0:
            print("⚠️ Список пуст.")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(list_models())