import asyncio
import os
import sys
from google import genai

# Добавляем путь к конфигу
sys.path.append(os.getcwd())
try:
    from config import Config
except ImportError:
    print("❌ Не могу найти config.py")
    exit()


async def check_keys():
    keys = Config.GEMINI_API_KEYS
    print(f"🔎 Проверка {len(keys)} ключей...\n")

    # Проверяем на самой стабильной модели
    model = "gemini-flash-latest"

    print(f"{'КЛЮЧ (конец)':<15} | {'СТАТУС':<20}")
    print("-" * 40)

    for api_key in keys:
        masked_key = f"...{api_key[-6:]}"
        client = genai.Client(api_key=api_key)

        try:
            await client.aio.models.generate_content(
                model=model,
                contents="Hello"
            )
            print(f"{masked_key:<15} | ✅ РАБОТАЕТ")
        except Exception as e:
            err = str(e)
            if "429" in err:
                print(f"{masked_key:<15} | ⛔ 429 (Лимит)")
            elif "400" in err or "403" in err:
                print(f"{masked_key:<15} | ❌ НЕВАЛИДНЫЙ")
            else:
                print(f"{masked_key:<15} | ⚠️ Ошибка: {err[:15]}...")


if __name__ == "__main__":
    asyncio.run(check_keys())