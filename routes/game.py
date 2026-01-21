from fastapi import APIRouter, HTTPException
from database import users_collection, lions_collection
from models import LevelCompleteRequest, UserResponse
from datetime import datetime
from bson import ObjectId

router = APIRouter()


@router.post("/complete_level", response_model=UserResponse)
async def complete_level(request: LevelCompleteRequest):
    # 1. Ищем пользователя
    try:
        user_id = ObjectId(request.userId)
    except:
        raise HTTPException(status_code=400, detail="Invalid User ID format")

    user = await users_collection.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Рассчитываем новые статы
    new_xp = user.get("xp", 0) + 50
    new_coins = user.get("knowledgeCoins", 0) + 10

    # Логика уровня (каждые 500 XP = новый уровень)
    current_level = user.get("level", 1)
    if new_xp >= current_level * 500:
        current_level += 1

    # 3. Обновляем User в БД
    await users_collection.update_one(
        {"_id": user_id},
        {"$set": {
            "xp": new_xp,
            "knowledgeCoins": new_coins,
            "level": current_level
        }}
    )

    # 4. Радуем Льва (если он есть)
    await lions_collection.update_one(
        {"userId": request.userId},
        {"$inc": {"happiness": 5}}  # +5 к счастью
    )

    # 5. Возвращаем обновленные данные
    updated_user = await users_collection.find_one({"_id": user_id})

    return UserResponse(
        id=str(updated_user["_id"]),
        nickname=updated_user.get("nickname", "User"),
        email=updated_user.get("email"),
        level=updated_user.get("level", 1),
        xp=updated_user.get("xp", 0),
        knowledgeCoins=updated_user.get("knowledgeCoins", 0),
        currentStreak=updated_user.get("currentStreak", 0),
        inventory=updated_user.get("inventory", [])
    )