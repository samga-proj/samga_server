from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/")
async def get_news():
    # 🔥 ИСПРАВЛЕНО: Данные теперь соответствуют Frontend (Stories UI)
    # Мы передаем цвета и иконки для градиентных карточек
    return [
        {
            "id": "1",
            "title": "Python",
            "subtitle": "Арсик кодит!",
            "description": "Наш лев теперь умеет писать код. Заходи в раздел 'Обучение'.",
            "icon": "code",
            "color_start": "0xFF2196F3",  # Blue 500
            "color_end": "0xFF673AB7",    # Deep Purple 500
            "date": datetime.now().isoformat()
        },
        {
            "id": "2",
            "title": "Дуэль",
            "subtitle": "Турнир знаний",
            "description": "Соревнуйся с другими студентами в режиме 'Дуэль'.",
            "icon": "flash_on",
            "color_start": "0xFFFF9800",  # Orange 500
            "color_end": "0xFFF44336",    # Red 500
            "date": datetime.now().isoformat()
        },
        {
            "id": "3",
            "title": "Советы",
            "subtitle": "Нет лени!",
            "description": "Арсик подготовил 5 советов, как не откладывать дела на потом.",
            "icon": "spa",
            "color_start": "0xFF4CAF50",  # Green 500
            "color_end": "0xFF009688",    # Teal 500
            "date": datetime.now().isoformat()
        },
        {
            "id": "4",
            "title": "Рейтинг",
            "subtitle": "Топ недели",
            "description": "Посмотри, кто занял первое место в лидерборде.",
            "icon": "emoji_events",
            "color_start": "0xFFFFD700",  # Gold
            "color_end": "0xFFFF6F00",    # Amber 900
            "date": datetime.now().isoformat()
        }
    ]