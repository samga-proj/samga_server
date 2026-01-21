from fastapi import APIRouter, HTTPException
from database import lions_collection
from models import LionResponse
from datetime import datetime

router = APIRouter()


@router.get("/{user_id}", response_model=LionResponse)
async def get_lion(user_id: str):
    # 1. Ищем льва в базе
    lion = await lions_collection.find_one({"userId": user_id})

    if lion:
        # Конвертируем _id в строку
        lion["id"] = str(lion["_id"])
        return lion

    # 2. Если льва нет, создаем нового (для новых пользователей)
    new_lion = {
        "userId": user_id,
        "name": "Arsik",
        "happiness": 80,
        "hunger": 50,
        "stage": "cub",
        "mood": "happy",
        "currentRoom": "yurt",
        "unlockedClothing": [],
        "unlockedRooms": ["yurt"],
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat()
    }

    result = await lions_collection.insert_one(new_lion)
    new_lion["id"] = str(result.inserted_id)

    return new_lion