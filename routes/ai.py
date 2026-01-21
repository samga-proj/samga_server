from fastapi import APIRouter
from pydantic import BaseModel
from google import genai
from config import Config
import random
import json
import asyncio

router = APIRouter()


# --- MODELS ---
class LessonRequest(BaseModel):
    topic: str
    style: str
    language: str


class QuizRequest(BaseModel):
    topic: str
    difficulty: str
    questions_count: int = 5


class ChatRequest(BaseModel):
    userId: str
    message: str


# --- LOGIC ---
async def generate_ultra_smart(prompt):
    """
    Умная генерация с защитой от 503 и перебором ключей.
    """
    available_keys = list(Config.GEMINI_API_KEYS)
    random.shuffle(available_keys)

    if not available_keys:
        print("❌ Ошибка: Нет ключей в .env")
        return None

    # Список моделей: пробуем стабильные, потом новые
    models_to_try = [
        "gemini-flash-latest",  # 1. Самая стабильная
        "gemini-1.5-flash",  # 2. Алиас
        "gemini-1.5-pro-latest",  # 3. PRO версия
        "gemini-2.0-flash-lite-preview-02-05",  # 4. Новинка
        "gemini-1.5-flash-8b",  # 5. Легкая
    ]

    print(f"🏁 Старт AI. Ключей: {len(available_keys)}")

    for i, api_key in enumerate(available_keys):
        client = genai.Client(api_key=api_key)
        key_short = f"...{api_key[-4:]}"

        for model_name in models_to_try:
            try:
                # print(f"👉 {key_short} -> {model_name}...")
                response = await client.aio.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                print(f"✅ УСПЕХ! {key_short} | {model_name}")
                return response.text

            except Exception as e:
                err = str(e)
                # Обработка перегрузки (503)
                if "503" in err:
                    print(f"   💤 {key_short}: 503 Перегрузка. Жду 1 сек...")
                    await asyncio.sleep(1)

                # Обработка лимитов (429)
                elif "429" in err:
                    pass

                    # Невалидный ключ
                elif "API_KEY_INVALID" in err:
                    print(f"   ❌ {key_short}: Невалидный ключ!")
                    break

                else:
                    print(f"   ⚠️ {key_short}: {err[:50]}...")

                continue

    print("💀 ВСЕ ключи и модели исчерпаны.")
    raise Exception("Global Quota Exceeded")


# --- ROUTES ---

@router.post("/chat")
async def chat_with_arsik(req: ChatRequest):
    try:
        reply = await generate_ultra_smart(
            f"Ты — Арсик, веселый ментор-львенок. Твой студент пишет: '{req.message}'. "
            "Отвечай кратко, с юмором и эмодзи."
        )
        return {"reply": reply}
    except:
        return {"reply": "Арсик спит 🦁💤 (Серверы заняты)"}


@router.post("/generate_lesson")
async def generate_lesson(req: LessonRequest):
    try:
        content = await generate_ultra_smart(
            f"Лекция: {req.topic}. Стиль: {req.style}. Язык: {req.language}. Markdown."
        )
        return {"content": content}
    except:
        return {"content": "Ошибка генерации лекции."}


@router.post("/generate_quiz")
async def generate_quiz(req: QuizRequest):
    try:
        # 🔥 ИЗМЕНЕНИЕ: ЖЕСТКИЙ ПРОМПТ
        prompt = (
            f"Создай тест на тему '{req.topic}'. Сложность: {req.difficulty}. "
            "Количество вопросов: СТРОГО 5 (ПЯТЬ). "
            "Не создавай 4, не создавай 6. Только 5. "
            "Формат JSON списка: "
            "[{"
            "  'question': 'Текст вопроса?', "
            "  'options': ['Вариант A', 'Вариант B', 'Вариант C', 'Вариант D'], "
            "  'correctIndices': [0], "
            "  'explanation': 'Объяснение...'"
            "}]"
            "Верни ТОЛЬКО валидный JSON, без markdown разметки."
        )

        response_text = await generate_ultra_smart(prompt)
        if not response_text: raise Exception("No response")

        # Очистка
        text = response_text.replace("```json", "").replace("```", "").strip()
        if text.startswith("JSON"): text = text[4:].strip()

        questions = json.loads(text)

        # 🔥 ГАРАНТИЯ "НЕ БОЛЬШЕ 5"
        if len(questions) > 5:
            questions = questions[:5]

        return {"questions": questions}

    except Exception as e:
        print(f"Quiz Error: {e}")
        return {"questions": []}