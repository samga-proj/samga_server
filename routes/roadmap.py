from fastapi import APIRouter, HTTPException, Query
from database import db
from typing import List, Optional
from pydantic import BaseModel
from google import genai
from config import Config
import json
import random
import asyncio

router = APIRouter()
collection = db.roadmaps


# --- MODELS ---
class LevelSchema(BaseModel):
    id: str
    number: int
    title: str
    description: str
    is_unlocked: bool = False
    is_completed: bool = False


class RoadmapSchema(BaseModel):
    id: str
    field_id: str
    field_name: str
    levels: List[LevelSchema]
    total_levels: int

    class Config:
        populate_by_name = True


class DailyTask(BaseModel):
    id: str
    topic: str
    description: str
    question: str
    xp: int
    isCompleted: bool = False


class DailyTasksResponse(BaseModel):
    title: str
    specId: str
    tasks: List[DailyTask]


class ValidateRequest(BaseModel):
    question: str
    user_answer: str


class ValidateResponse(BaseModel):
    isCorrect: bool
    feedback: str
    xp_awarded: int = 0


# --- SMART AI HELPER (Точно такой же, как в чате) ---
async def generate_with_retry(prompt: str):
    """
    Генерация с защитой от сбоев: перебирает ключи и модели.
    """
    available_keys = list(Config.GEMINI_API_KEYS)
    random.shuffle(available_keys)

    if not available_keys:
        print("❌ Ошибка: Нет ключей в .env")
        return None

    models_to_try = [
        "gemini-flash-latest",
        "gemini-1.5-flash",
        "gemini-1.5-pro-latest",
        "gemini-2.0-flash-lite-preview-02-05",
        "gemini-1.5-flash-8b",
    ]

    for api_key in available_keys:
        client = genai.Client(api_key=api_key)
        key_short = f"...{api_key[-4:]}"

        for model_name in models_to_try:
            try:
                # print(f"👉 Roadmap AI: {key_short} -> {model_name}...")
                response = await client.aio.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                return response.text

            except Exception as e:
                err = str(e)
                if "503" in err:
                    await asyncio.sleep(1)
                elif "429" in err:
                    pass
                elif "API_KEY_INVALID" in err:
                    break
                continue

    print("💀 Roadmap AI: Все ключи исчерпаны.")
    return None


# --- ЗАГЛУШКА (Если AI умер) ---
def _get_mock_tasks(specId: str):
    return {
        "title": "Оффлайн Тренировка 🦁",
        "specId": specId,
        "tasks": [
            DailyTask(id="m1", topic="Теория", description=f"Повтори основы {specId}.", question="Что повторил?",
                      xp=20),
            DailyTask(id="m2", topic="Практика", description="Напиши 10 строк кода.", question="Что написал?", xp=30),
            DailyTask(id="m3", topic="Отдых", description="Дай глазам отдохнуть.", question="Готов продолжить?", xp=10)
        ]
    }


# --- ROUTES ---

# 1. 🔥 УМНЫЕ ЕЖЕДНЕВНЫЕ ЗАДАЧИ
@router.get("/daily_tasks/", response_model=DailyTasksResponse)
async def get_daily_tasks(
        specId: str = Query(..., description="ID специализации (например, python_basic)"),
        userId: str = Query(..., description="ID пользователя")
):
    # Темы настроения для разнообразия
    vibes = [
        "сегодня мы углубляемся в детали",
        "день жесткой практики",
        "время искать баги и фиксить их",
        "режим архитектора: строим правильно",
        "легкий день, закрепляем базу"
    ]
    current_vibe = random.choice(vibes)

    # 🔥 ПРОМПТ: ТРЕБУЕМ РАЗНООБРАЗИЕ ПО ТЕМЕ
    prompt = (
        f"Ты — Арсик, ментор по программированию. Студент изучает курс: '{specId}'. "
        f"Настрой дня: {current_vibe}. "
        "Твоя задача: Придумать 3 (ТРИ) ежедневных задания ИМЕННО ПО ЭТОЙ ТЕМЕ. "
        "\nСТРУКТУРА ЗАДАНИЙ (Обязательно разные типы):"
        "1. 📘 Теория (Concept): Задание прочитать или изучить конкретную тему внутри курса."
        "2. 💻 Практика (Code): Задание написать мини-скрипт или функцию."
        "3. 🐞 Челлендж/Дебаг (Challenge): Найти ошибку или оптимизировать что-то."
        "\nТРЕБОВАНИЯ:"
        "- Пиши весело, используй эмодзи и сленг."
        "- В поле 'question' задавай вопрос, на который студент должен ответить текстом."
        "- Не давай общих заданий типа 'попей воды', только по теме учебы!"
        "\nФОРМАТ JSON:"
        "{'title': 'Мотивирующий заголовок', 'tasks': ["
        "{'topic': 'Теория: [Тема]', 'description': '...', 'question': '...', 'xp': 30},"
        "{'topic': 'Практика: [Тема]', 'description': '...', 'question': '...', 'xp': 50},"
        "{'topic': 'Челлендж', 'description': '...', 'question': '...', 'xp': 70}"
        "]}"
    )

    response_text = await generate_with_retry(prompt)

    # Если AI не ответил, возвращаем заглушку
    if not response_text:
        return _get_mock_tasks(specId)

    try:
        # Чистим ответ
        text = response_text.replace("```json", "").replace("```", "").strip()
        if text.startswith("JSON"): text = text[4:].strip()

        data = json.loads(text)

        tasks_list = []
        for item in data.get("tasks", []):
            tasks_list.append(DailyTask(
                id=f"ai_{userId}_{random.randint(10000, 99999)}",
                topic=item.get("topic", "Задание"),
                description=item.get("description", "Выполни это."),
                question=item.get("question", "Готово?"),
                xp=item.get("xp", 50)
            ))

        return {
            "title": data.get("title", f"Дейлики: {specId}"),
            "specId": specId,
            "tasks": tasks_list[:3]  # Гарантируем не больше 3
        }

    except Exception as e:
        print(f"Parsing Error: {e}")
        return _get_mock_tasks(specId)


# 2. ПРОВЕРКА ОТВЕТА
@router.post("/validate_answer", response_model=ValidateResponse)
async def validate_answer(req: ValidateRequest):
    prompt = (
        f"Вопрос ментора: {req.question}\n"
        f"Ответ студента: {req.user_answer}\n"
        "Ты — Арсик. Оцени ответ. Правильно ли студент понял тему? "
        "Верни JSON: {'isCorrect': true/false, 'feedback': 'Короткий веселый комментарий'}."
    )

    response_text = await generate_with_retry(prompt)

    if not response_text:
        return {"isCorrect": True, "feedback": "Связь прервалась, но засчитываю авансом! 🦁", "xp_awarded": 20}

    try:
        text = response_text.replace("```json", "").replace("```", "").strip()
        if text.startswith("JSON"): text = text[4:].strip()
        result = json.loads(text)

        return {
            "isCorrect": result.get('isCorrect', False),
            "feedback": result.get('feedback', 'Принято!'),
            "xp_awarded": 50 if result.get('isCorrect') else 0
        }
    except:
        return {"isCorrect": True, "feedback": "Ответ принят!", "xp_awarded": 20}


# 3. ПОЛУЧЕНИЕ КАРТЫ (Из базы)
@router.get("/{field_id}", response_model=RoadmapSchema)
async def get_roadmap(field_id: str):
    roadmap = await collection.find_one({"field_id": field_id})
    if not roadmap:
        raise HTTPException(status_code=404, detail=f"Roadmap not found")
    roadmap["id"] = str(roadmap["_id"])
    return roadmap