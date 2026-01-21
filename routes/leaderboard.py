from fastapi import APIRouter
from database import users_collection
from typing import List
from pydantic import BaseModel

router = APIRouter()


# Модель ответа (то, что полетит на телефон)
class LeaderboardUser(BaseModel):
    username: str
    level: int
    knowledgeCoins: int


@router.get("/", response_model=List[LeaderboardUser])
async def get_leaderboard():
    # 1. Ищем всех пользователей в MongoDB
    # 2. Сортируем по 'knowledgeCoins' (убывание: -1)
    # 3. Берем только 50 человек
    cursor = users_collection.find().sort("knowledgeCoins", -1).limit(50)
    users = await cursor.to_list(length=50)

    results = []
    for user in users:
        results.append({
            # В базе поле называется 'name', а фронтенд ждет 'username'
            "username": user.get("name", "Аноним"),
            "level": user.get("level", 1),
            "knowledgeCoins": user.get("knowledgeCoins", 0)
        })

    return results