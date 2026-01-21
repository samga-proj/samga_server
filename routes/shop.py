from fastapi import APIRouter, HTTPException
from database import users_collection, lions_collection
from models import BuyRequest
from typing import List, Dict
from bson import ObjectId

router = APIRouter()

# --- MOCK DATA (Товары) ---
# В реальном проекте это хранилось бы в БД в коллекции 'items'
SHOP_ITEMS = [
    # ЕДА
    {"id": "food_meat", "name": "Сочный стейк", "price": 50, "category": "food", "effect": 20, "icon": "🥩"},
    {"id": "food_fish", "name": "Рыбка", "price": 30, "category": "food", "effect": 10, "icon": "🐟"},
    {"id": "food_apple", "name": "Яблоко", "price": 15, "category": "food", "effect": 5, "icon": "🍎"},

    # ОДЕЖДА
    {"id": "cloth_cape", "name": "Супер-плащ", "price": 500, "category": "clothing", "icon": "🦸"},
    {"id": "cloth_glasses", "name": "Умные очки", "price": 250, "category": "clothing", "icon": "👓"},
    {"id": "cloth_hat", "name": "Шляпа мага", "price": 300, "category": "clothing", "icon": "🎩"},

    # КОМНАТЫ (Фоны)
    {"id": "room_space", "name": "Космос", "price": 1000, "category": "room", "icon": "🚀"},
    {"id": "room_loft", "name": "Лофт", "price": 800, "category": "room", "icon": "🏙️"},
]


@router.get("/", response_model=List[Dict])
async def get_shop_items():
    return SHOP_ITEMS


@router.post("/buy")
async def buy_item(req: BuyRequest):
    # 1. Проверяем пользователя
    try:
        user_id = ObjectId(req.userId)
    except:
        raise HTTPException(status_code=400, detail="Invalid User ID")

    user = await users_collection.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Проверяем баланс
    current_coins = user.get("knowledgeCoins", 0)  # или "coins"
    if current_coins < req.price:
        raise HTTPException(status_code=400, detail="Недостаточно монет!")

    # 3. Списываем монеты и обновляем инвентарь пользователя
    new_balance = current_coins - req.price

    # Обновляем User
    await users_collection.update_one(
        {"_id": user_id},
        {
            "$set": {"knowledgeCoins": new_balance},
            "$addToSet": {"inventory": req.itemId}
        }
    )

    # 4. Применяем эффекты на Льва (кормление или гардероб)
    lion_update = {}

    if req.category == "food":
        # Находим товар, чтобы узнать эффект (восстановление сытости)
        item = next((i for i in SHOP_ITEMS if i["id"] == req.itemId), None)
        effect = item["effect"] if item else 10

        # Увеличиваем сытость (hunger) и счастье, но не больше 100
        # MongoDB позволяет использовать операторы агрегации в update, но для простоты используем $inc
        # (в идеале нужно проверять max 100, но пока просто прибавим)
        lion_update = {
            "$inc": {"hunger": effect, "happiness": 5}
        }

    elif req.category == "clothing":
        lion_update = {
            "$addToSet": {"unlockedClothing": req.itemId}
        }

    elif req.category == "room":
        lion_update = {
            "$addToSet": {"unlockedRooms": req.itemId}
        }

    if lion_update:
        await lions_collection.update_one(
            {"userId": req.userId},
            lion_update
        )

    return {
        "success": True,
        "message": f"Куплено: {req.itemId}",
        "newBalance": new_balance
    }